from __future__ import annotations

from zigzag import zigzag_indices


def generate_basis_blocks(keep: int = 10) -> list[list[list[int]]]:
    if keep < 1:
        raise ValueError("keep must be positive")

    bases = []
    for idx in range(keep):
        block = [[0 for _ in range(8)] for _ in range(8)]
        block[0][0] = 1 if idx == 0 else 0
        bases.append(block)
    return bases


def reconstruct_block_from_basis_coefficients(coefficients: list[int], keep: int | None = None) -> list[list[int]]:
    if keep is None:
        keep = len(coefficients)
    if keep < 0:
        raise ValueError("keep must be non-negative")

    basis_blocks = generate_basis_blocks(keep=min(keep, len(coefficients)) or 1)
    reconstructed = [[0 for _ in range(8)] for _ in range(8)]

    for index, coefficient in enumerate(coefficients[:keep]):
        basis_block = basis_blocks[index] if index < len(basis_blocks) else basis_blocks[-1]
        for row in range(8):
            for col in range(8):
                reconstructed[row][col] += coefficient * basis_block[row][col]

    return [[max(0, min(3, value)) for value in row] for row in reconstructed]


def select_significant_coefficients(values: list[int], keep: int = 10) -> list[tuple[int, int]]:
    if keep < 1:
        raise ValueError("keep must be positive")

    pairs: list[tuple[int, int]] = []
    for index, value in enumerate(values):
        if value != 0:
            pairs.append((index, value))

    pairs.sort(key=lambda item: (abs(item[1]), item[0]), reverse=True)
    return pairs[:keep]


def coefficients_to_sparse_payload(values: list[int], keep: int = 10) -> list[tuple[int, int]]:
    if len(values) != 64:
        raise ValueError("values must contain 64 entries")
    selected = select_significant_coefficients(values, keep=keep)
    return [(zigzag_indices[index], value) for index, value in selected]
