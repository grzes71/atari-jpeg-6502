from pathlib import Path

from decode_simple import decode_simple_j650
from encoder import encode_image
from image_io import load_binary_image_2bpp


def test_raw_bitmap_to_j650_output():
    image = load_binary_image_2bpp(r"C:\Temp\witcher3.bin", width=160, height=192)
    output = Path("tests/data/out_test.j650")
    encode_image(image, output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_raw_bitmap_payload_can_be_decoded_back():
    image = load_binary_image_2bpp(r"C:\Temp\witcher3.bin", width=160, height=192)
    output = Path("tests/data/out_test_roundtrip.j650")
    encode_image(image, output)
    decoded = decode_simple_j650(output)
    assert len(decoded) == 192
    assert len(decoded[0]) == 160
