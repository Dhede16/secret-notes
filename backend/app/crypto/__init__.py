from Crypto.Cipher import AES as PyCryptoDOME_AES
from app.crypto.aes import key_expansion, encrypt_block, decrypt_block
from app.crypto.modes import encrypt_cbc, decrypt_cbc, generate_iv, pad_pkcs7, unpad_pkcs7


def cross_check_aes(key: bytes, plaintext: bytes) -> bool:
    """Cross-check our AES encryption with pycryptodome."""
    cipher = PyCryptoDOME_AES.new(key, PyCryptoDOME_AES.MODE_ECB)
    pycrypto_ct = cipher.encrypt(plaintext)
    our_ct, _ = encrypt_block(plaintext, key_expansion(key))
    return pycrypto_ct == our_ct


def cross_check_cbc(key: bytes, plaintext: bytes, iv: bytes) -> bool:
    """Cross-check our CBC encryption with pycryptodome."""
    cipher = PyCryptoDOME_AES.new(key, PyCryptoDOME_AES.MODE_CBC, iv)
    pycrypto_ct = cipher.encrypt(pad_pkcs7(plaintext))
    our_ct = encrypt_cbc(plaintext, key, iv)
    return pycrypto_ct == our_ct


def cross_check_cbc_decrypt(key: bytes, ciphertext: bytes, iv: bytes, expected_plaintext: bytes) -> bool:
    """Cross-check our CBC decryption with pycryptodome."""
    cipher = PyCryptoDOME_AES.new(key, PyCryptoDOME_AES.MODE_CBC, iv)
    pycrypto_pt = cipher.decrypt(ciphertext)
    from app.crypto.modes import unpad_pkcs7
    our_pt = decrypt_cbc(ciphertext, key, iv)
    return unpad_pkcs7(pycrypto_pt) == our_pt == expected_plaintext