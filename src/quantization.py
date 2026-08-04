from __future__ import annotations


DEFAULT_QUANT_TABLE = [
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99],
]


def to_q88(value: int) -> int:
    return int(round(value * 256))


def from_q88(value: int) -> int:
    return int(round(value / 256))


def quantize_block(block: list[list[int]]) -> list[list[int]]:
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    quantized: list[list[int]] = []
    for row_index, row in enumerate(block):
        quantized_row: list[int] = []
        for col_index, value in enumerate(row):
            scaled = from_q88(to_q88(value // DEFAULT_QUANT_TABLE[row_index][col_index]))
            clipped = max(-128, min(127, int(scaled)))
            quantized_row.append(clipped)
        quantized.append(quantized_row)
    return quantized


def dequantize_block(block: list[list[int]]) -> list[list[int]]:
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    dequantized: list[list[int]] = []
    for row_index, row in enumerate(block):
        dequantized_row: list[int] = []
        for col_index, value in enumerate(row):
            restored = from_q88(to_q88(value) * DEFAULT_QUANT_TABLE[row_index][col_index])
            dequantized_row.append(int(restored))
        dequantized.append(dequantized_row)
    return dequantized


def quantize_block_with_table(block: list[list[int]], table: list[list[int]]) -> list[list[int]]:
    """Quantize an 8×8 block using a custom quantization table."""
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    quantized: list[list[int]] = []
    for row_index, row in enumerate(block):
        quantized_row: list[int] = []
        for col_index, value in enumerate(row):
            divisor = max(1, table[row_index][col_index])
            scaled = from_q88(to_q88(value // divisor))
            clipped = max(-128, min(127, int(scaled)))
            quantized_row.append(clipped)
        quantized.append(quantized_row)
    return quantized


def dequantize_block_with_table(block: list[list[int]], table: list[list[int]]) -> list[list[int]]:
    """Dequantize an 8×8 block using a custom quantization table."""
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    dequantized: list[list[int]] = []
    for row_index, row in enumerate(block):
        dequantized_row: list[int] = []
        for col_index, value in enumerate(row):
            restored = from_q88(to_q88(value) * table[row_index][col_index])
            dequantized_row.append(int(restored))
        dequantized.append(dequantized_row)
    return dequantized
