from pathlib import Path

from decode_simple import decode_simple_j650
from encoder import encode_image
from image_io import load_binary_image_2bpp


def test_decode_simple_j650_roundtrip():
    image = load_binary_image_2bpp(r"C:\Temp\witcher3.bin", width=160, height=192)
    path = Path("tests/data/roundtrip.j650")
    encode_image(image, path)
    decoded = decode_simple_j650(path)
    assert len(decoded) == 192
    assert len(decoded[0]) == 160
    assert decoded[0][0] == decoded[1][1]


def test_decode_simple_j650_roundtrips_single_block_image(tmp_path):
    image = [[(row * 2 + col) % 4 for col in range(8)] for row in range(8)]
    out_path = tmp_path / "single_block.j650"

    encode_image(image, out_path)
    decoded = decode_simple_j650(out_path)

    assert len(decoded) == 8
    assert all(len(row) == 8 for row in decoded)
    assert decoded == image
    assert all(0 <= value <= 3 for row in decoded for value in row)
