from pathlib import Path

import pytest

from decoder_model import decode_block_payload
from encoder import encode_block, encode_image
from fileformat import HEADER_SIZE, J650FormatError, build_simple_block_payload, read_header, write_header


def test_header_roundtrip():
    payload = write_header(width=160, height=192, block_size=8)

    assert payload[:4] == b"J650"
    assert len(payload) == HEADER_SIZE

    header = read_header(payload)
    assert header["magic"] == "J650"
    assert header["width"] == 160
    assert header["height"] == 192
    assert header["block_size"] == 8
    assert header["reserved"] == 0


def test_encode_empty_block():
    block = [[0 for _ in range(8)] for _ in range(8)]
    assert encode_block(block) == b"\xff"


def test_encode_image_with_empty_blocks(tmp_path):
    image = [[0 for _ in range(160)] for _ in range(192)]
    output_path = tmp_path / "test.j650"

    encode_image(image, output_path)

    assert output_path.exists()
    payload = output_path.read_bytes()
    assert payload.startswith(b"J650")
    assert len(payload) > HEADER_SIZE


def test_build_simple_block_payload_has_tag_and_length():
    payload = build_simple_block_payload([0] * 64)

    assert payload[0] == 0x01
    assert payload[1] == 0x03
    assert payload[2:] == b"@\x00\xff"


def test_build_simple_block_payload_packs_two_bit_block_values():
    values = [0, 1, 2, 3] * 16
    payload = build_simple_block_payload(values, keep=64)

    assert payload[0] == 0x01
    assert payload[1] == 16
    assert len(payload) == 18
    assert decode_block_payload(payload) == values


def test_encode_block_payload_changes_with_keep_coeffs():
    block = [[0 for _ in range(8)] for _ in range(8)]
    for row in range(8):
        for col in range(8):
            block[row][col] = 1 if (row + col) % 2 == 0 else 0

    payload_small = encode_block(block, keep_coeffs=1)
    payload_mid = encode_block(block, keep_coeffs=6)
    payload_large = encode_block(block, keep_coeffs=64)

    assert len(payload_small) < len(payload_mid)
    assert len(payload_mid) < len(payload_large)

def test_read_header_rejects_invalid_magic():
    payload = b"BAD!" + (0).to_bytes(2, "little") + (0).to_bytes(2, "little") + bytes([8, 0, 0, 0])

    with pytest.raises(J650FormatError):
        read_header(payload)


def test_read_header_rejects_zero_dimensions():
    payload = b"J650" + (0).to_bytes(2, "little") + (0).to_bytes(2, "little") + bytes([8, 0, 0, 0])

    with pytest.raises(J650FormatError):
        read_header(payload)


def test_read_header_rejects_unsupported_block_size():
    payload = b"J650" + (1).to_bytes(2, "little") + (1).to_bytes(2, "little") + bytes([4, 0, 0, 0])

    with pytest.raises(J650FormatError):
        read_header(payload)
