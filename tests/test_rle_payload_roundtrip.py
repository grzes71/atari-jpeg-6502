from pathlib import Path

from decoder_model import decode_block_payload
from fileformat import build_simple_block_payload
from rle import decode_rle


def test_simple_block_payload_roundtrips_to_values():
    values = [0, 0, 0, 3, 3, 3, 0, 0, 2, 0, 0, 0]
    payload = build_simple_block_payload(values + [0] * (64 - len(values)))

    assert payload[0] == 0x01
    assert payload[1] == 16
    assert decode_block_payload(payload) == values + [0] * (64 - len(values))


def test_decode_rle_stops_on_eob_marker():
    payload = bytes([0x03, 0x00, 0x02, 0x07, 0x01, 0xFF])

    decoded = decode_rle(payload)

    assert decoded == [0, 0, 0, 7, 7]
    assert 0xFF not in decoded


def test_build_simple_block_payload_embeds_zero_block_marker():
    payload = build_simple_block_payload([0] * 64)

    assert payload[0:2] == b"\x01\x03"
    assert payload[2:] == b"@\x00\xFF"
