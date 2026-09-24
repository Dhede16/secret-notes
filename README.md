# SecretNotes

Aplikasi catatan rahasia berbasis enkripsi AES-128 dengan antarmuka web.

## Arsitektur

```
Vue.js 3 (Frontend)  <->  FastAPI (Backend REST)  <->  Supabase (PostgreSQL)
```

## Struktur Proyek

```
secret-notes/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Environment configuration
│   │   ├── db.py              # Supabase client (lazy init)
│   │   ├── crypto/
│   │   │   ├── aes.py         # Manual AES-128 implementation (FIPS-197)
│   │   │   ├── kdf.py         # PBKDF2 key derivation + bcrypt PIN hashing
│   │   │   ├── modes.py       # AES-CBC mode + PKCS#7 padding
│   │   │   └── __init__.py    # Cross-check helpers vs pycryptodome
│   │   ├── session.py         # In-memory session and key store
│   │   ├── schemas.py         # Pydantic models
│   │   ├── routes/
│   │   │   ├── auth.py        # /auth/setup, /auth/unlock, /auth/lock
│   │   │   └── notes.py       # CRUD + AES lab endpoints
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_aes.py        # 16 AES unit tests (FIPS-197 KAT + pycryptodome)
│   │   └── test_e2e.py        # 13 end-to-end crypto pipeline tests
│   ├── schema.sql             # Supabase database schema
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml         # Package configuration
│   └── .env.example           # Environment template
├── frontend/
│   ├── src/
│   │   ├── main.ts            # Vue app entry point
│   │   ├── App.vue            # Root component
│   │   ├── router/            # Vue Router with auth guard
│   │   ├── stores/            # Pinia stores (auth, notes)
│   │   ├── api/               # API client with token injection
│   │   ├── composables/       # useIdleLock auto-lock composable
│   │   ├── views/             # LockView, NotesView, NoteEditorView, AesLabView
│   │   └── components/        # AppButton, AppInput, AppCard, HexMatrix, TimerIndicator, NoteCard
│   └── package.json
└── PRD.md                   # Product Requirements Document
```

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with Supabase credentials
python -m app.main  # or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database (Supabase)

```sql
-- Run schema.sql in Supabase SQL Editor
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/setup` | Create PIN (first time only) |
| POST | `/api/auth/unlock` | Unlock with PIN, returns session token |
| POST | `/api/auth/lock` | Lock session, deletes AES key |
| GET | `/api/notes` | List notes (titles decrypted) |
| POST | `/api/notes` | Create new note |
| GET | `/api/notes/{id}` | Get note with decrypted content |
| PUT | `/api/notes/{id}` | Update note (new IV) |
| DELETE | `/api/notes/{id}` | Delete note |
| GET | `/api/notes/{id}/aes-log` | AES visualization data |
| GET | `/api/notes/{id}/round-keys` | Key expansion visualization |

## Encryption Details

- **Key Derivation**: PBKDF2-HMAC-SHA256 (100,000 iterations, 16 bytes)
- **PIN Hashing**: bcrypt (12 rounds)
- **Cipher**: AES-128-CBC with PKCS#7 padding
- **IV**: Random 16 bytes per note
- **Storage**: Ciphertext and IV stored as base64 in Supabase

## Verification

```bash
cd backend
python -m pytest tests/ -v  # 29 tests: 16 AES + 13 e2e
```

- FIPS-197 KAT #1: ✅ Pass
- Cross-check with pycryptodome: ✅ Pass
- Encrypt/Decrypt roundtrip: ✅ Pass
- FIPS round key 1 = `a0fafe1788542cb123a339392a6c7605`: ✅ Pass

## FIPS-197 Known Answer Test (KAT #1)

- Key: `2b7e151628aed2a6abf7158809cf4f3c`
- Plaintext: `3243f6a8885a308d313198a2e0370734`
- Ciphertext: `3925841d02dc09fbdc118597196a0b32`
- Round Key 1: `a0fafe1788542cb123a339392a6c7605`

## License

Academic project — D3 Teknik Informatika