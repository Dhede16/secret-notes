import hashlib
import os
import bcrypt

KDF_ITERATIONS = 100000
KDF_KEY_LENGTH = 16  # AES-128


def derive_key(pin: str, salt: bytes) -> bytes:
    """
    Derive an AES-128 key from a PIN using PBKDF2-HMAC-SHA256.
    Returns 16 bytes (AES-128 key).
    """
    pin_bytes = pin.encode('utf-8')
    key = hashlib.pbkdf2_hmac('sha256', pin_bytes, salt, KDF_ITERATIONS, dklen=KDF_KEY_LENGTH)
    return key


def hash_pin(pin: str) -> str:
    """
    Hash a PIN using bcrypt. Returns the bcrypt hash string.
    The PIN is never stored as plaintext.
    """
    pin_bytes = pin.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pin_bytes, salt).decode('utf-8')


def verify_pin(pin: str, pin_hash: str) -> bool:
    """
    Verify a PIN against a bcrypt hash. Returns True if the PIN matches.
    """
    pin_bytes = pin.encode('utf-8')
    return bcrypt.checkpw(pin_bytes, pin_hash.encode('utf-8'))


def generate_salt() -> bytes:
    """Generate a random 16-byte salt for KDF."""
    return os.urandom(16)


def salt_to_base64(salt: bytes) -> str:
    """Convert salt bytes to base64 string for storage."""
    import base64
    return base64.b64encode(salt).decode('utf-8')


def base64_to_salt(salt_b64: str) -> bytes:
    """Convert base64 string back to salt bytes."""
    import base64
    return base64.b64decode(salt_b64)