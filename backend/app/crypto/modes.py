import os

BLOCK_SIZE = 16  # AES block size in bytes


def pad_pkcs7(data: bytes) -> bytes:
    """
    Pad data to a multiple of BLOCK_SIZE using PKCS#7 padding.
    If data is already a multiple, adds a full block of padding.
    """
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    if pad_len == 0:
        pad_len = BLOCK_SIZE
    return data + bytes([pad_len] * pad_len)


def unpad_pkcs7(padded: bytes) -> bytes:
    """
    Remove PKCS#7 padding from data.
    Returns the unpadded data.
    Raises ValueError if padding is invalid.
    """
    if len(padded) == 0 or len(padded) % BLOCK_SIZE != 0:
        raise ValueError("Invalid padded data length")
    pad_len = padded[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding length")
    if padded[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding bytes")
    return padded[:-pad_len]


def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Encrypt plaintext using AES-128-CBC with PKCS#7 padding.
    Returns ciphertext (includes padding).
    """
    from app.crypto.aes import encrypt_block, key_expansion

    if len(key) != 16:
        raise ValueError(f"Key must be 16 bytes, got {len(key)}")
    if len(iv) != 16:
        raise ValueError(f"IV must be 16 bytes, got {len(iv)}")

    padded = pad_pkcs7(plaintext)
    round_keys = key_expansion(key)
    ciphertext = b''
    prev_block = iv

    for i in range(0, len(padded), BLOCK_SIZE):
        block = padded[i:i + BLOCK_SIZE]
        # XOR with previous ciphertext block
        xored = bytes(block[j] ^ prev_block[j] for j in range(BLOCK_SIZE))
        encrypted = encrypt_block(xored, round_keys)[0]
        ciphertext += encrypted
        prev_block = encrypted

    return ciphertext


def decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Decrypt ciphertext using AES-128-CBC.
    Returns plaintext with PKCS#7 padding removed.
    """
    from app.crypto.aes import decrypt_block, key_expansion

    if len(key) != 16:
        raise ValueError(f"Key must be 16 bytes, got {len(key)}")
    if len(iv) != 16:
        raise ValueError(f"IV must be 16 bytes, got {len(iv)}")
    if len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Ciphertext length must be multiple of block size")

    round_keys = key_expansion(key)
    plaintext = b''
    prev_block = iv

    for i in range(0, len(ciphertext), BLOCK_SIZE):
        block = ciphertext[i:i + BLOCK_SIZE]
        decrypted = decrypt_block(block, round_keys)
        xored = bytes(decrypted[j] ^ prev_block[j] for j in range(BLOCK_SIZE))
        plaintext += xored
        prev_block = block

    return unpad_pkcs7(plaintext)


def generate_iv() -> bytes:
    """Generate a random 16-byte IV."""
    return os.urandom(16)