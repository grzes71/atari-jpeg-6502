from pathlib import Path

from image_io import load_binary_image_1bpp, load_binary_image_2bpp


def test_2bpp_loader_reads_simple_pattern():
    path = Path("tests/data/sample_2bpp.bin")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes([0xAA, 0x55, 0x00, 0x00]))

    pixels = load_binary_image_2bpp(path, width=4, height=2)
    assert pixels[0][0] == 2
    assert pixels[0][1] == 2
    assert pixels[1][0] == 1
    assert pixels[1][1] == 1


def test_1bpp_loader_reads_simple_pattern():
    path = Path("tests/data/sample_1bpp.bin")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes([0b10101010]))

    pixels = load_binary_image_1bpp(path, width=8, height=1)
    assert pixels[0][0] == 1
    assert pixels[0][1] == 0
    assert pixels[0][7] == 0
