from __future__ import annotations

import math

from quantization import dequantize_block
from zigzag import zigzag_indices


def _cosine(value: float) -> float:
    return math.cos(value)


def forward_dct_2d(block: list[list[int]]) -> list[list[float]]:
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    rows = [[float(value) for value in row] for row in block]
    coeffs: list[list[float]] = []
    for u in range(8):
        coeff_row: list[float] = []
        for v in range(8):
            cu = 1 / math.sqrt(2) if u == 0 else 1.0
            cv = 1 / math.sqrt(2) if v == 0 else 1.0
            total = 0.0
            for x in range(8):
                for y in range(8):
                    angle_x = math.pi * (2 * x + 1) * u / 16.0
                    angle_y = math.pi * (2 * y + 1) * v / 16.0
                    total += rows[x][y] * _cosine(angle_x) * _cosine(angle_y)
            coeff_row.append(0.25 * cu * cv * total)
        coeffs.append(coeff_row)
    return coeffs


def inverse_dct_2d(coeffs: list[list[float]]) -> list[list[float]]:
    if not coeffs or len(coeffs) != 8 or any(len(row) != 8 for row in coeffs):
        raise ValueError("coeffs must be an 8x8 matrix")

    reconstructed: list[list[float]] = []
    for x in range(8):
        row: list[float] = []
        for y in range(8):
            total = 0.0
            for u in range(8):
                cu = 1 / math.sqrt(2) if u == 0 else 1.0
                for v in range(8):
                    cv = 1 / math.sqrt(2) if v == 0 else 1.0
                    angle_x = math.pi * (2 * x + 1) * u / 16.0
                    angle_y = math.pi * (2 * y + 1) * v / 16.0
                    total += coeffs[u][v] * cu * cv * _cosine(angle_x) * _cosine(angle_y)
            row.append(0.25 * total)
        reconstructed.append(row)
    return reconstructed


def reconstruct_block_from_coefficients(coefficients: list[int], keep: int | None = None) -> list[list[int]]:
    if keep is None:
        keep = len(coefficients)
    if keep < 0:
        raise ValueError("keep must be non-negative")

    coeff_values = [0] * 64
    for idx, coeff in enumerate(coefficients[:keep]):
        coeff_values[zigzag_indices[idx]] = coeff

    coeff_matrix = [[coeff_values[y * 8 + x] for x in range(8)] for y in range(8)]
    reconstructed = inverse_dct_2d(coeff_matrix)
    dequantized = dequantize_block([[int(round(value)) for value in row] for row in reconstructed])
    return [[max(0, min(3, value)) for value in row] for row in dequantized]
