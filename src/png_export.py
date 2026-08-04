from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image

from fileformat import HEADER_SIZE, read_header
from decoder_model import decode_block_payload
from rgb2a8.atari_palette import atari_index_to_rgb, rgb_to_atari_index


def _resolve_palette(palette_colors: Iterable[int] | None) -> list[tuple[int, int, int]]:
    if palette_colors is None:
        return [atari_index_to_rgb(index) for index in range(16)]

    values = list(palette_colors)
    if len(values) == 0:
        return [(0, 0, 0)] * 16

    if len(values) == 1:
        values = values * 4
    if len(values) == 2:
        values = values + [values[0], values[1]]
    if len(values) == 3:
        values = values + [values[2]]
    if len(values) > 4:
        values = values[:4]

    resolved: list[tuple[int, int, int]] = []
    for value in values:
        if isinstance(value, (tuple, list)) and len(value) == 3:
            resolved.append((int(value[0]), int(value[1]), int(value[2])))
        else:
            try:
                resolved.append(atari_index_to_rgb(int(value) & 0xFF))
            except ValueError:
                resolved.append((0, 0, 0))
    if len(resolved) < 16:
        resolved = resolved + [(0, 0, 0)] * (16 - len(resolved))
    return resolved[:16]


def _pack_pixels_to_screen_ram(pixels: list[list[int]], mode: str) -> bytes:
    mode = mode.upper()
    if mode in {"D", "E"}:
        width = len(pixels[0])
        height = len(pixels)
        screen_bytes = bytearray((width * height) // 4)
        for y in range(height):
            for x in range(0, width, 4):
                byte_index = (y * width + x) // 4
                byte_value = 0
                for offset in range(4):
                    if x + offset >= width:
                        value = 0
                    else:
                        value = pixels[y][x + offset] & 0x03
                    byte_value |= (value & 0x03) << (6 - offset * 2)
                screen_bytes[byte_index] = byte_value
        return bytes(screen_bytes)

    if mode == "F":
        width = len(pixels[0])
        height = len(pixels)
        screen_bytes = bytearray((width * height) // 8)
        for y in range(height):
            for x in range(0, width, 8):
                byte_index = (y * width + x) // 8
                byte_value = 0
                for offset in range(8):
                    if x + offset >= width:
                        value = 0
                    else:
                        value = pixels[y][x + offset] & 0x01
                    byte_value |= (value & 0x01) << (7 - offset)
                screen_bytes[byte_index] = byte_value
        return bytes(screen_bytes)

    raise ValueError("unsupported ANTIC mode")


def decompress(compressed_bytes: bytes, antic_mode: str = "E") -> bytes:
    if len(compressed_bytes) < HEADER_SIZE:
        raise ValueError("compressed data is too short")

    header = read_header(compressed_bytes)
    width = int(header["width"])
    height = int(header["height"])
    payload = compressed_bytes[HEADER_SIZE:]

    blocks_per_row = (width + 7) // 8
    blocks_per_col = (height + 7) // 8
    block_count = blocks_per_row * blocks_per_col

    image_pixels: list[list[int]] = [[0 for _ in range(width)] for _ in range(height)]
    offset = 0
    for block_index in range(block_count):
        if offset >= len(payload):
            break

        if payload[offset] == 0xFF:
            values = [0] * 64
            offset += 1
        else:
            block_len = payload[offset + 1] if offset + 1 < len(payload) else 0
            block_bytes = payload[offset : offset + 2 + block_len]
            values = decode_block_payload(block_bytes)
            offset += 2 + block_len

        block_row = (block_index // blocks_per_row) * 8
        block_col = (block_index % blocks_per_row) * 8
        for row_index in range(8):
            for col_index in range(8):
                pixel_row = block_row + row_index
                pixel_col = block_col + col_index
                if pixel_row >= height or pixel_col >= width:
                    continue
                if antic_mode.upper() in {"D", "E"}:
                    image_pixels[pixel_row][pixel_col] = values[row_index * 8 + col_index] & 0x03
                else:
                    image_pixels[pixel_row][pixel_col] = values[row_index * 8 + col_index] & 0x01

    return _pack_pixels_to_screen_ram(image_pixels, antic_mode)


def _expand_pixels(screen_bytes: bytes, mode: str, width: int, height: int) -> list[list[int]]:
    mode = mode.upper()
    pixels: list[list[int]] = []

    if mode in {"D", "E"}:
        for row in range(height):
            row_pixels: list[int] = []
            for col in range(0, width, 4):
                byte_index = (row * (width // 4)) + (col // 4)
                if byte_index < len(screen_bytes):
                    byte = screen_bytes[byte_index]
                else:
                    byte = 0
                row_pixels.extend([
                    (byte >> 6) & 0x03,
                    (byte >> 4) & 0x03,
                    (byte >> 2) & 0x03,
                    byte & 0x03,
                ])
            pixels.append(row_pixels[:width])
        return pixels

    if mode == "F":
        for row in range(height):
            row_pixels: list[int] = []
            for col in range(0, width, 8):
                byte_index = (row * (width // 8)) + (col // 8)
                if byte_index < len(screen_bytes):
                    byte = screen_bytes[byte_index]
                else:
                    byte = 0
                for bit_idx in range(7, -1, -1):
                    row_pixels.append((byte >> bit_idx) & 0x01)
            pixels.append(row_pixels[:width])
        return pixels

    raise ValueError("unsupported ANTIC mode")


def screen_to_png(screen_bytes: bytes, mode: str, palette_colors: Iterable[int] | None, output_path: str | Path, scale: int = 2) -> Path:
    if scale not in {1, 2, 4}:
        raise ValueError("scale must be one of 1, 2, 4")

    mode = mode.upper()
    if mode == "D":
        width, height = 160, 96
    elif mode == "E":
        width, height = 160, 192
    elif mode == "F":
        width, height = 320, 192
    else:
        raise ValueError("unsupported ANTIC mode")

    pixels = _expand_pixels(screen_bytes, mode, width, height)
    palette = _resolve_palette(palette_colors)
    rgb_pixels = [
        [
            (palette[pixel][0], palette[pixel][1], palette[pixel][2]) if pixel < len(palette) else (0, 0, 0)
            for pixel in row
        ]
        for row in pixels
    ]

    image = Image.new("RGB", (width, height), color=(0, 0, 0))
    image.putdata([value for row in rgb_pixels for value in row])

    if scale > 1:
        image = image.resize((width * scale, height * scale), Image.Resampling.NEAREST)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    return output
