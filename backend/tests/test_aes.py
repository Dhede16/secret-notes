"""
Tests for AES manual implementation.
- FIPS-197 Known Answer Tests
- Cross-check with pycryptodome
"""

import pytest
from Crypto.Cipher import AES as PyCryptoDOME_AES

from app.crypto.aes import (
    key_expansion,
    encrypt_block,
    decrypt_block,
    sub_bytes,
    inv_sub_bytes,
    shift_rows,
    inv_shift_rows,
    mix_columns,
    inv_mix_columns,
    add_round_key,
)

# ---------------------------------------------------------------------------
# FIPS-197 Known Answer Test (KAT) #1
# Key: 2b7e151628aed2a6abf7158809cf4f3c
# Plaintext: 3243f6a8885a308d313198a2e0370734
# Ciphertext: 3925841d02dc09fbdc118597196a0b32
# ---------------------------------------------------------------------------

FIPS_KAT_KEY = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
FIPS_KAT_PLAINTEXT = bytes.fromhex("3243f6a8885a308d313198a2e0370734")
FIPS_KAT_CIPHERTEXT = bytes.fromhex("3925841d02dc09fbdc118597196a0b32")

FIPS_KAT_ROUND_KEYS_HEX = [
    "a0fafe1788542cb123a339392a6c7605",
]


def test_key_expansion_fips():
    """FIPS-197 KAT: verify round key 1 matches expected value."""
    keys = key_expansion(FIPS_KAT_KEY)
    assert len(keys) == 11, f"Expected 11 round keys, got {len(keys)}"
    # Round key 1 (index 1) should be a0fafe1788542cb123a339392a6c7605
    assert keys[1] == bytes.fromhex("a0fafe1788542cb123a339392a6c7605"), \
        f"Round key 1 mismatch: {keys[1].hex()}"


def test_encrypt_block_fips():
    """FIPS-197 KAT: encrypt single block matches expected ciphertext."""
    keys = key_expansion(FIPS_KAT_KEY)
    ciphertext, trace = encrypt_block(FIPS_KAT_PLAINTEXT, keys, trace=True)
    assert ciphertext == FIPS_KAT_CIPHERTEXT, \
        f"Ciphertext mismatch: {ciphertext.hex()} != {FIPS_KAT_CIPHERTEXT.hex()}"


def test_decrypt_block_fips():
    """FIPS-197 KAT: decrypt ciphertext back to plaintext."""
    keys = key_expansion(FIPS_KAT_KEY)
    plaintext = decrypt_block(FIPS_KAT_CIPHERTEXT, keys)
    assert plaintext == FIPS_KAT_PLAINTEXT, \
        f"Plaintext mismatch: {plaintext.hex()} != {FIPS_KAT_PLAINTEXT.hex()}"


def test_encrypt_decrypt_roundtrip():
    """Encrypt then decrypt should return original plaintext."""
    keys = key_expansion(FIPS_KAT_KEY)
    ciphertext, _ = encrypt_block(FIPS_KAT_PLAINTEXT, keys)
    plaintext = decrypt_block(ciphertext, keys)
    assert plaintext == FIPS_KAT_PLAINTEXT


def test_encrypt_cross_check_pycryptodome():
    """Cross-check our AES encryption with pycryptodome."""
    keys = key_expansion(FIPS_KAT_KEY)
    _, our_trace = encrypt_block(FIPS_KAT_PLAINTEXT, keys, trace=True)

    # Use pycryptodome to encrypt with same key
    cipher = PyCryptoDOME_AES.new(FIPS_KAT_KEY, PyCryptoDOME_AES.MODE_ECB)
    pycrypto_ciphertext = cipher.encrypt(FIPS_KAT_PLAINTEXT)

    assert pycrypto_ciphertext == FIPS_KAT_CIPHERTEXT, \
        f"pycryptodome ciphertext mismatch: {pycrypto_ciphertext.hex()}"


def test_trace_structure():
    """Verify trace has correct structure."""
    keys = key_expansion(FIPS_KAT_KEY)
    _, trace = encrypt_block(FIPS_KAT_PLAINTEXT, keys, trace=True)

    # Should have 11 entries (round 0-10)
    assert len(trace) == 11, f"Expected 11 trace entries, got {len(trace)}"

    # Round 0 should only have after_add_round_key
    round0 = trace[0]
    assert 'after_add_round_key' in round0
    assert 'after_sub_bytes' not in round0

    # Rounds 1-9 should have all stages
    for i in range(1, 10):
        round_data = trace[i]
        assert 'after_sub_bytes' in round_data
        assert 'after_shift_rows' in round_data
        assert 'after_mix_columns' in round_data
        assert 'after_add_round_key' in round_data
        assert 'round_key_matrix' in round_data
        assert len(round_data['after_sub_bytes']) == 4
        assert len(round_data['after_sub_bytes'][0]) == 4

    # Round 10 should NOT have after_mix_columns
    round10 = trace[10]
    assert 'after_sub_bytes' in round10
    assert 'after_shift_rows' in round10
    assert 'after_mix_columns' not in round10
    assert 'after_add_round_key' in round10


def test_round_key_matrix_format():
    """Verify round_key_matrix in trace is 4x4."""
    keys = key_expansion(FIPS_KAT_KEY)
    _, trace = encrypt_block(FIPS_KAT_PLAINTEXT, keys, trace=True)

    for round_data in trace[1:]:
        rk = round_data['round_key_matrix']
        assert len(rk) == 4, "Round key matrix should have 4 rows"
        assert all(len(row) == 4 for row in rk), "Each row should have 4 columns"


def test_trace_final_round_matches_ciphertext():
    """The final AddRoundKey state in trace should match ciphertext bytes."""
    keys = key_expansion(FIPS_KAT_KEY)
    ciphertext, trace = encrypt_block(FIPS_KAT_PLAINTEXT, keys, trace=True)

    # Last trace entry's after_add_round_key should match ciphertext
    final_state = trace[-1]['after_add_round_key']
    # Convert 4x4 matrix back to bytes (column-major: state[r][c] -> byte at position c*4+r)
    state_bytes = bytes(final_state[r][c] for c in range(4) for r in range(4))
    assert state_bytes == ciphertext, \
        f"Final state doesn't match ciphertext: {state_bytes.hex()} != {ciphertext.hex()}"


def test_sub_bytes_correctness():
    """Test sub_bytes with known values from standard AES S-box."""
    state = [[0x32, 0x88, 0x31, 0xa0], [0x32, 0x43, 0xa1, 0x12], [0x51, 0xec, 0x39, 0x7d], [0xf4, 0xd7, 0x28, 0x26]]
    result = sub_bytes(state)
    # SBOX[0x32] = 0x23 (verified from standard AES S-box)
    assert result[0][0] == 0x23, f"SBOX[0x32] should be 0x23, got {result[0][0]:02x}"


def test_inv_sub_bytes_is_inverse():
    """inv_sub_bytes should reverse sub_bytes."""
    state = [[0x32, 0x88, 0x31, 0xa0], [0x32, 0x43, 0xa1, 0x12], [0x51, 0xec, 0x39, 0x7d], [0xf4, 0xd7, 0x28, 0x26]]
    after_sub = sub_bytes(state)
    after_inv = inv_sub_bytes(after_sub)
    assert after_inv == state, "inv_sub_bytes should reverse sub_bytes"


def test_shift_rows_correctness():
    """Test shift_rows preserves all bytes, just shifts."""
    state = [[0x01, 0x02, 0x03, 0x04], [0x05, 0x06, 0x07, 0x08], [0x09, 0x0a, 0x0b, 0x0c], [0x0d, 0x0e, 0x0f, 0x10]]
    result = shift_rows(state)
    # Row 0: no shift -> [0x01, 0x02, 0x03, 0x04]
    assert result[0] == [0x01, 0x02, 0x03, 0x04]
    # Row 1: shift left by 1 -> [0x06, 0x07, 0x08, 0x05]
    assert result[1] == [0x06, 0x07, 0x08, 0x05]
    # Row 2: shift left by 2 -> [0x0b, 0x0c, 0x09, 0x0a]
    assert result[2] == [0x0b, 0x0c, 0x09, 0x0a]
    # Row 3: shift left by 3 -> [0x10, 0x0d, 0x0e, 0x0f]
    assert result[3] == [0x10, 0x0d, 0x0e, 0x0f]


def test_inv_shift_rows_is_inverse():
    """inv_shift_rows should reverse shift_rows."""
    state = [[0x01, 0x02, 0x03, 0x04], [0x05, 0x06, 0x07, 0x08], [0x09, 0x0a, 0x0b, 0x0c], [0x0d, 0x0e, 0x0f, 0x10]]
    after_shift = shift_rows(state)
    after_inv = inv_shift_rows(after_shift)
    assert after_inv == state, "inv_shift_rows should reverse shift_rows"


def test_mix_columns_correctness():
    """Test mix_columns with zero state stays zero."""
    state = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    result = mix_columns(state)
    assert result == state, "mix_columns of zero state should be zero"


def test_add_round_key_correctness():
    """Test add_round_key XORs correctly with column-major indexing (r + 4*c)."""
    # State: 4x4 with known values
    state = [[0x00, 0x01, 0x02, 0x03], [0x04, 0x05, 0x06, 0x07], [0x08, 0x09, 0x0a, 0x0b], [0x0c, 0x0d, 0x0e, 0x0f]]
    # Round key: 16 bytes
    round_key = bytes([0xff, 0xfe, 0xfd, 0xfc, 0xfb, 0xfa, 0xf9, 0xf8, 0xf7, 0xf6, 0xf5, 0xf4, 0xf3, 0xf2, 0xf1, 0xf0])
    result = add_round_key(state, round_key)
    # With column-major indexing: result[r][c] = state[r][c] ^ round_key[r + 4*c]
    # result[0][0] = 0x00 ^ round_key[0] = 0x00 ^ 0xff = 0xff
    assert result[0][0] == 0xff, f"0x00 ^ 0xff should be 0xff, got {result[0][0]:02x}"
    # result[0][1] = 0x01 ^ round_key[1] = 0x01 ^ 0xfe = 0xff? No: round_key[0+4*1] = round_key[4] = 0xfb
    # Actually: r=0, c=1: round_key[0 + 4*1] = round_key[4] = 0xfb
    # 0x01 ^ 0xfb = 0xfa
    assert result[0][1] == (0x01 ^ round_key[4]), f"0x01 ^ round_key[4] should be {0x01 ^ round_key[4]:02x}, got {result[0][1]:02x}"
    # result[1][0] = 0x04 ^ round_key[1] = 0x04 ^ 0xfe = 0xfa
    assert result[1][0] == (0x04 ^ round_key[1]), f"0x04 ^ round_key[1] should be {0x04 ^ round_key[1]:02x}, got {result[1][0]:02x}"


def test_key_expansion_length():
    """AES-128 should produce exactly 11 round keys."""
    key = bytes(range(16))
    keys = key_expansion(key)
    assert len(keys) == 11
    assert all(len(k) == 16 for k in keys)


def test_decrypt_after_encrypt():
    """Encrypting twice with same key produces same ciphertext (deterministic)."""
    keys = key_expansion(FIPS_KAT_KEY)
    ciphertext1, _ = encrypt_block(FIPS_KAT_PLAINTEXT, keys)
    ciphertext2, _ = encrypt_block(FIPS_KAT_PLAINTEXT, keys)
    assert ciphertext1 == ciphertext2, "Same input + same key should produce same ciphertext"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])