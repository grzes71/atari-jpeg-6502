from __future__ import annotations

from pathlib import Path

from block_utils import split_image_into_blocks
from fileformat import HEADER_SIZE, build_simple_block_payload, write_block, write_header


def encode_block(block: list[list[int]], keep_coeffs: int = 10) -> bytes:
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    flat = [value for row in block for value in row]
    if all(value == 0 for value in flat):
        return b"\xff"

    payload = build_simple_block_payload(flat, keep=keep_coeffs)
    return write_block(payload)


def encode_image(image: list[list[int]], output_path: str | Path, keep_coeffs: int = 10) -> Path:
    if not image or not image[0]:
        raise ValueError("image cannot be empty")

    width = len(image[0])
    height = len(image)
    if any(len(row) != width for row in image):
        raise ValueError("image rows must have equal width")

    payload = bytearray(write_header(width=width, height=height, block_size=8))

    for block in split_image_into_blocks(image, block_size=8):
        payload.extend(encode_block(block, keep_coeffs=keep_coeffs))

    path = Path(output_path)
    path.write_bytes(payload)
    return path
