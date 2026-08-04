from __future__ import annotations

from typing import List


def split_image_into_blocks(image: list[list[int]], block_size: int = 8) -> list[list[list[int]]]:
    if not image or not image[0]:
        raise ValueError("image cannot be empty")

    height = len(image)
    width = len(image[0])
    if any(len(row) != width for row in image):
        raise ValueError("image rows must have equal width")

    blocks: list[list[list[int]]] = []
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            block = [row[x : x + block_size] for row in image[y : y + block_size]]
            block = [row + [0] * (block_size - len(row)) for row in block]
            while len(block) < block_size:
                block.append([0] * block_size)
            blocks.append(block)
    return blocks
