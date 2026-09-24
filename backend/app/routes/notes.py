from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.schemas import NoteListItem, Note, AesLog, RoundKeys, ErrorResponse, NoteCreateResponse
from app.db import get_supabase
from app.session import session_store
from app.crypto.aes import decrypt_block, key_expansion, encrypt_block
from app.crypto.modes import encrypt_cbc, decrypt_cbc, generate_iv
from app.config import DEBUG
import base64

router = APIRouter()


def get_session_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ")[1]
    if not session_store.validate_session(token):
        raise HTTPException(status_code=401, detail="Session expired or locked")
    return token


def get_key_from_token(token: str):
    key = session_store.get_key(token)
    if not key:
        raise HTTPException(status_code=401, detail="Session key expired")
    return key


def decrypt_field(ciphertext_b64: str, iv_b64: str, key: bytes, round_keys: list):
    ct = base64.b64decode(ciphertext_b64)
    iv = base64.b64decode(iv_b64)
    pt_bytes = decrypt_cbc(ct, key, iv, round_keys)
    return pt_bytes.decode('utf-8')


@router.get("/", response_model=list[NoteListItem])
async def list_notes(authorization: str = Depends(get_session_token)):
    key = get_key_from_token(authorization)
    round_keys = key_expansion(key)

    result = get_supabase().table("notes").select("*").order("updated_at", desc=True).execute()
    notes = []
    for row in result.data:
        title = decrypt_field(row["title_ciphertext"], row["title_iv"], key, round_keys)
        notes.append({
            "id": row["id"],
            "title": title,
            "updated_at": row["updated_at"],
        })
    return notes


@router.post("/", response_model=NoteCreateResponse)
async def create_note(request: dict, authorization: str = Depends(get_session_token)):
    key = get_key_from_token(authorization)
    round_keys = key_expansion(key)

    title_iv = generate_iv()
    title_ct = encrypt_cbc(request["title"].encode('utf-8'), key, title_iv, round_keys)
    body_iv = generate_iv()
    body_ct = encrypt_cbc(request["body"].encode('utf-8'), key, body_iv, round_keys)

    result = get_supabase().table("notes").insert({
        "title_ciphertext": base64.b64encode(title_ct).decode('utf-8'),
        "title_iv": base64.b64encode(title_iv).decode('utf-8'),
        "body_ciphertext": base64.b64encode(body_ct).decode('utf-8'),
        "body_iv": base64.b64encode(body_iv).decode('utf-8'),
    }).execute()

    note_id = result.data[0]["id"] if result.data else None
    return {"id": note_id}


@router.get("/{note_id}", response_model=Note)
async def get_note(note_id: str, authorization: str = Depends(get_session_token)):
    key = get_key_from_token(authorization)
    round_keys = key_expansion(key)

    result = get_supabase().table("notes").select("*").eq("id", note_id).limit(1).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    row = result.data[0]
    title = decrypt_field(row["title_ciphertext"], row["title_iv"], key, round_keys)
    body = decrypt_field(row["body_ciphertext"], row["body_iv"], key, round_keys)

    return Note(
        id=row["id"], title=title, body=body,
        created_at=row["created_at"], updated_at=row["updated_at"],
    )


@router.put("/{note_id}")
async def update_note(note_id: str, request: dict, authorization: str = Depends(get_session_token)):
    key = get_key_from_token(authorization)
    round_keys = key_expansion(key)

    title_iv = generate_iv()
    title_ct = encrypt_cbc(request["title"].encode('utf-8'), key, title_iv, round_keys)
    body_iv = generate_iv()
    body_ct = encrypt_cbc(request["body"].encode('utf-8'), key, body_iv, round_keys)

    get_supabase().table("notes").update({
        "title_ciphertext": base64.b64encode(title_ct).decode('utf-8'),
        "title_iv": base64.b64encode(title_iv).decode('utf-8'),
        "body_ciphertext": base64.b64encode(body_ct).decode('utf-8'),
        "body_iv": base64.b64encode(body_iv).decode('utf-8'),
    }).eq("id", note_id).execute()
    return {}


@router.delete("/{note_id}", status_code=204)
async def delete_note(note_id: str, authorization: str = Depends(get_session_token)):
    get_supabase().table("notes").delete().eq("id", note_id).execute()


@router.get("/{note_id}/aes-log", response_model=AesLog)
async def get_aes_log(note_id: str, authorization: str = Depends(get_session_token)):
    key = get_key_from_token(authorization)

    result = get_supabase().table("notes").select("body_ciphertext", "body_iv").eq("id", note_id).limit(1).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    row = result.data[0]
    ciphertext = base64.b64decode(row["body_ciphertext"])
    iv = base64.b64decode(row["body_iv"])
    round_keys = key_expansion(key)

    from app.crypto.modes import decrypt_cbc
    plaintext_full = decrypt_cbc(ciphertext, key, iv, round_keys)
    first_block = plaintext_full[:16]

    _, trace = encrypt_block(first_block, round_keys, trace=True)

    return AesLog(
        block_index=0,
        input_matrix=[[first_block[c * 4 + r] for c in range(4)] for r in range(4)],
        rounds=trace,
    )


@router.get("/{note_id}/round-keys", response_model=RoundKeys)
async def get_round_keys(note_id: str, authorization: str = Depends(get_session_token)):
    key = get_key_from_token(authorization)
    round_keys = key_expansion(key)

    # Build round key matrices (each round key is 16 bytes = 4x4 matrix)
    round_key_matrices = []
    for i in range(11):
        rk_bytes = round_keys[i]
        matrix = [[rk_bytes[c * 4 + r] for c in range(4)] for r in range(4)]
        round_key_matrices.append(matrix)

    # Build key expansion trace
    key_expansion_trace = []
    from app.crypto.aes import SBOX, RCON
    words = [list(key[i * 4:(i + 1) * 4]) for i in range(4)]
    Nk, Nb, Nr = 4, 4, 10

    for i in range(4, Nb * (Nr + 1)):
        temp = words[-1][:]
        is_rotword = False
        is_subword = False
        is_rcon = False
        rcon_val = None

        if len(words) % Nk == 0:
            is_rotword = True
            temp = temp[1:] + temp[:1]
            temp = [SBOX[b] for b in temp]
            is_subword = True
            rcon_index = len(words) // Nk - 1
            temp[0] ^= RCON[rcon_index]
            is_rcon = True
            rcon_val = RCON[rcon_index]

        new_word = [words[len(words) - Nk][j] ^ temp[j] for j in range(4)]
        words.append(new_word)
        key_expansion_trace.append({
            "word_index": i,
            "is_rotword": is_rotword,
            "is_subword": is_subword,
            "is_rcon": is_rcon,
            "round_constant": rcon_val,
        })

    return RoundKeys(
        round_keys=round_key_matrices,
        key_expansion_trace=key_expansion_trace,
    )