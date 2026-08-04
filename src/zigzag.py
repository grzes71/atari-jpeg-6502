from __future__ import annotations

zigzag_indices = [
    0, 1, 8, 16, 9, 2, 3, 10,
    17, 24, 32, 25, 18, 11, 4, 5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13, 6, 7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63,
]


def zigzag_extract(block: list[list[int]], keep: int = 10) -> list[int]:
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    flat = [block[y][x] for y, x in ((index // 8, index % 8) for index in zigzag_indices)]
    return flat[:keep]


def coefficients_to_block_values(coefficients: list[int], keep: int | None = None) -> list[int]:
    if keep is None:
        keep = len(coefficients)
    if keep < 0:
        raise ValueError("keep must be non-negative")

    values = [0] * 64
    for idx, coeff in enumerate(coefficients[:keep]):
        values[zigzag_indices[idx]] = coeff
    return values
