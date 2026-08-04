from __future__ import annotations

from pathlib import Path

from decoder_model import decode_block_payload
from fileformat import HEADER_SIZE, J650FormatError, read_header


def decode_simple_j650(path: str | Path) -> list[list[int]]:
    payload = Path(path).read_bytes()
    header = read_header(payload)
    width = int(header["width"])
    height = int(header["height"])

    data = payload[HEADER_SIZE:]
    image: list[list[int]] = []
    index = 0

    for _ in range(height):
        row: list[int] = []
        for _ in range(width):
            row.append(0)
        image.append(row)

    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if index >= len(data):
                break
            block_tag = data[index]
            index += 1
            if block_tag == 0xFF:
                continue
            if block_tag != 0x01:
                raise J650FormatError(f"unsupported block payload tag: {block_tag:#x}")
            if index >= len(data):
                raise J650FormatError("block payload is missing length")
            block_length = data[index]
            index += 1
            payload_bytes = data[index : index + block_length]
            index += block_length
            values = decode_block_payload(bytes([0x01, block_length]) + payload_bytes)
            if not values:
                values = [0] * 64
            if len(values) < 64:
                values = values + [0] * (64 - len(values))
            for row in range(8):
                for col in range(8):
                    if y + row < height and x + col < width:
                        image[y + row][x + col] = values[row * 8 + col]
    return image
