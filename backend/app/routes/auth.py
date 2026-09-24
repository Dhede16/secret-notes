from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.schemas import SetupPinRequest, UnlockRequest, AuthResponse, ErrorResponse
from app.config import SUPABASE_SERVICE_KEY
from app.db import get_supabase
from app.crypto.kdf import hash_pin, verify_pin, generate_salt, salt_to_base64, base64_to_salt, derive_key
from app.session import session_store
import time

router = APIRouter()


@router.post("/setup", response_model=AuthResponse, responses={400: {"model": ErrorResponse}})
async def setup_pin(request: SetupPinRequest):
    if len(request.pin) < 6:
        raise HTTPException(status_code=400, detail="PIN must be at least 6 characters")

    try:
        result = get_supabase().table("app_settings").select("id").limit(1).execute()
        if result.data and len(result.data) > 0:
            raise HTTPException(status_code=400, detail="PIN already set up")
    except Exception:
        pass

    pin_hash = hash_pin(request.pin)
    kdf_salt = salt_to_base64(generate_salt())

    try:
        get_supabase().table("app_settings").insert({
            "pin_hash": pin_hash,
            "kdf_salt": kdf_salt,
            "idle_timeout_sec": 180,
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup: {str(e)}")

    token = session_store.create_session()
    return AuthResponse(token=token, expires_in=3600)


@router.post("/unlock", response_model=AuthResponse, responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
async def unlock(request: UnlockRequest):
    if len(request.pin) < 6:
        raise HTTPException(status_code=400, detail="PIN must be at least 6 characters")

    try:
        result = get_supabase().table("app_settings").select("*").limit(1).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="PIN not set up")

        settings = result.data[0]
        pin_hash = settings["pin_hash"]
        kdf_salt = base64_to_salt(settings["kdf_salt"])

        if not verify_pin(request.pin, pin_hash):
            raise HTTPException(status_code=401, detail="Invalid PIN")

        key = derive_key(request.pin, kdf_salt)
        token = session_store.create_session()
        session_store.store_key(token, key, time.time() + 3600)

        return AuthResponse(token=token, expires_in=3600)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lock", status_code=204, responses={401: {"model": ErrorResponse}})
async def lock(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    token = authorization.split(" ")[1]
    if not session_store.validate_session(token):
        raise HTTPException(status_code=401, detail="Session expired or locked")
    session_store.lock(token)
    return None