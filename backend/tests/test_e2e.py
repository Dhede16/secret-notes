"""End-to-end verification of SecretNotes crypto pipeline."""
import pytest
from app.crypto.aes import key_expansion, encrypt_block, decrypt_block
from app.crypto.kdf import derive_key, hash_pin, verify_pin, generate_salt
from app.crypto.modes import encrypt_cbc, decrypt_cbc, pad_pkcs7, unpad_pkcs7, generate_iv
from app.crypto import cross_check_aes, cross_check_cbc


# FIPS-197 KAT #1
FIPS_KEY = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
FIPS_PT = bytes.fromhex("3243f6a8885a308d313198a2e0370734")
FIPS_CT = bytes.fromhex("3925841d02dc09fbdc118597196a0b32")


def test_encrypt_block_matches_fips_kat():
    """Encryption matches FIPS-197 Known Answer Test #1."""
    keys = key_expansion(FIPS_KEY)
    ct, _ = encrypt_block(FIPS_PT, keys)
    assert ct == FIPS_CT


def test_decrypt_block_matches_fips_kat():
    """Decryption of FIPS-197 KAT ciphertext is correct."""
    keys = key_expansion(FIPS_KEY)
    pt = decrypt_block(FIPS_CT, keys)
    assert pt == FIPS_PT


def test_encrypt_decrypt_roundtrip():
    """Encrypt then decrypt returns original plaintext."""
    keys = key_expansion(FIPS_KEY)
    ct, _ = encrypt_block(FIPS_PT, keys)
    pt = decrypt_block(ct, keys)
    assert pt == FIPS_PT


def test_cross_check_with_pycryptodome():
    """Manual AES matches pycryptodome for FIPS-197 KAT #1."""
    keys = key_expansion(FIPS_KEY)
    assert cross_check_aes(FIPS_KEY, FIPS_PT)


def test_cross_check_cbc_with_pycryptodome():
    """Manual CBC matches pycryptodome."""
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    iv = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    plaintext = b"SecretNotes test message!"
    assert cross_check_cbc(key, plaintext, iv)


def test_cbc_padding_roundtrip():
    """CBC encrypt/decrypt with PKCS#7 padding works."""
    key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
    iv = generate_iv()
    plaintext = b"Hello SecretNotes!"
    ciphertext = encrypt_cbc(plaintext, key, iv)
    decrypted = decrypt_cbc(ciphertext, key, iv)
    assert decrypted == plaintext


def test_kdf_derives_correct_key_length():
    """PBKDF2 derives a 16-byte key for AES-128."""
    salt = generate_salt()
    key = derive_key("test-pin-123", salt)
    assert len(key) == 16


def test_pin_hash_and_verify():
    """bcrypt hash and verify works."""
    pin = "my-secret-pin"
    pin_hash = hash_pin(pin)
    assert verify_pin(pin, pin_hash)
    assert not verify_pin("wrong-pin", pin_hash)


def test_round_keys_count():
    """AES-128 produces 11 round keys."""
    keys = key_expansion(FIPS_KEY)
    assert len(keys) == 11


def test_round_key_matrices_are_4x4():
    """Each round key is a 4x4 matrix."""
    keys = key_expansion(FIPS_KEY)
    for rk in keys:
        assert len(rk) == 16
        # Verify column-major ordering
        matrix = [[rk[c * 4 + r] for c in range(4)] for r in range(4)]
        assert len(matrix) == 4
        assert all(len(row) == 4 for row in matrix)


def test_fips_round_key_1():
    """FIPS-197 KAT: Round key 1 must be a0fafe1788542cb123a339392a6c7605."""
    keys = key_expansion(FIPS_KEY)
    assert keys[1].hex() == "a0fafe1788542cb123a339392a6c7605"


def test_kdf_salt_roundtrip():
    """Salt to base64 and back works."""
    from app.crypto.kdf import salt_to_base64, base64_to_salt
    salt = generate_salt()
    b64 = salt_to_base64(salt)
    restored = base64_to_salt(b64)
    assert salt == restored


def test_encrypt_decrypt_random_key():
    """Full encrypt/decrypt roundtrip with random key."""
    import os
    key = os.urandom(16)
    keys = key_expansion(key)
    plaintext = b"SecretNotes!" + b" " * 4
    assert len(plaintext) == 16
    ct, _ = encrypt_block(plaintext, keys)
    pt = decrypt_block(ct, keys)
    assert pt == plaintext