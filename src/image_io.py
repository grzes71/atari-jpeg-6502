from __future__ import annotations

from pathlib import Path


def load_binary_image(path: str | Path, width: int, height: int, bpp: int) -> list[list[int]]:
    data = Path(path).read_bytes()
    expected_bytes = (width * height * bpp + 7) // 8
    if len(data) < expected_bytes:
        raise ValueError(f"expected at least {expected_bytes} bytes for {width}x{height} image at {bpp} bpp")

    pixels: list[list[int]] = []
    bit_index = 0
    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            if byte_index >= len(data):
                row.append(0)
                bit_index += bpp
                continue

            value = 0
            for shift in range(bpp):
                bit_pos = bit_offset + shift
                if bit_pos >= 8:
                    next_byte_index = byte_index + 1
                    if next_byte_index >= len(data):
                        break
                    bits = ((data[byte_index] << 8) | data[next_byte_index]) >> (8 - bit_pos)
                else:
                    bits = data[byte_index] >> (7 - bit_pos)
                if bit_pos < 8:
                    value |= ((bits & 0x01) << (bpp - 1 - shift))
            row.append(value & ((1 << bpp) - 1))
            bit_index += bpp
        pixels.append(row)
    return pixels


def load_binary_image_2bpp(path: str | Path, width: int, height: int) -> list[list[int]]:
    return load_binary_image(path, width=width, height=height, bpp=2)


def load_binary_image_1bpp(path: str | Path, width: int, height: int) -> list[list[int]]:
    return load_binary_image(path, width=width, height=height, bpp=1)


def write_representative_binary_image(path: str | Path, width: int, height: int, bpp: int = 2) -> Path:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    expected_bytes = (width * height * bpp + 7) // 8
    data = bytearray(expected_bytes)
    for y in range(height):
        for x in range(width):
            value = (x + y) % 4
            bit_index = (y * width + x) * bpp
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            shift = 8 - bit_offset - bpp
            if shift < 0:
                data[byte_index] |= (value & ((1 << bpp) - 1)) << (8 + shift)
                data[byte_index + 1] |= (value & ((1 << bpp) - 1)) >> (bpp + shift)
            else:
                data[byte_index] |= (value & ((1 << bpp) - 1)) << shift

    output_path = Path(path)
    output_path.write_bytes(data)
    return output_path
