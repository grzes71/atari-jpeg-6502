from rle import EOB, decode_rle, encode_rle


def test_encode_rle_roundtrip_for_zero_and_nonzero_runs():
    values = [0, 0, 0, 3, 3, 3, 0, 0, 4, 0, 0, 0]

    encoded = encode_rle(values)
    decoded = decode_rle(encoded)

    assert decoded == values
    assert encoded.startswith(b"\x03\x00")
    assert encoded.endswith(bytes([EOB]))
