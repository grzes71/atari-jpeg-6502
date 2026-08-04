from __future__ import annotations

from pathlib import Path
from typing import Sequence

from adaptive_quantization import get_quantization_table
from ai_selector import SelectionConfig, select_coefficients
from block_utils import split_image_into_blocks
from dct import forward_dct_2d, inverse_dct_2d, reconstruct_block_from_coefficients
from fileformat import HEADER_SIZE, build_simple_block_payload, build_sparse_coefficient_payload, write_block, write_header
from quantization import dequantize_block, dequantize_block_with_table, quantize_block, quantize_block_with_table
from zigzag import zigzag_indices


def encode_block(block: list[list[int]], keep_coeffs: int = 10) -> bytes:
    if not block or len(block) != 8 or any(len(row) != 8 for row in block):
        raise ValueError("block must be an 8x8 matrix")

    flat = [value for row in block for value in row]
    if all(value == 0 for value in flat):
        return b"\xff"

    payload = build_simple_block_payload(flat, keep=keep_coeffs)
    return write_block(payload)


def encode_block_dct(
    block: list[list[int]],
    keep_coeffs: int = 10,
    strategy: str = "hybrid",
    quant_table: str = "default",
    selector_config: SelectionConfig | None = None,
) -> bytes:
    """Encode an 8×8 block using DCT + AI-assisted coefficient selection.

    Parameters
    ----------
    block:
        8×8 pixel block.
    keep_coeffs:
        Number of coefficients to keep (ignored when *strategy* is ``"hybrid"``
        and *selector_config* enables adaptive counts).
    strategy:
        One of ``"zigzag"``, ``"magnitude"``, ``"hybrid"``.
    quant_table:
        Name of the quantization table (``"default"``, ``"aggressive"``,
        ``"balanced"``, ``"fine"``).
    selector_config:
        Fine-grained configuration for ``"hybrid"`` strategy.
    """
    table = get_quantization_table(quant_table)

    dct_coeffs = forward_dct_2d(block)
    dct_rounded = [[int(round(v)) for v in row] for row in dct_coeffs]
    q_block = quantize_block_with_table(dct_rounded, table)

    selection = select_coefficients(
        q_block,
        strategy=strategy,
        keep=keep_coeffs,
        config=selector_config,
    )

    if not selection.selected_indices or all(v == 0 for v in selection.selected_values):
        return b"\xff"

    nonzero_indices: list[int] = []
    nonzero_values: list[int] = []
    for idx, val in zip(selection.selected_indices, selection.selected_values):
        if val != 0:
            nonzero_indices.append(idx)
            nonzero_values.append(val)

    if not nonzero_indices:
        return b"\xff"

    return write_block(
        build_sparse_coefficient_payload(
            indices=nonzero_indices,
            values=nonzero_values,
        )
    )


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


def encode_image_dct(
    image: list[list[int]],
    output_path: str | Path,
    keep_coeffs: int = 10,
    strategy: str = "hybrid",
    quant_table: str = "default",
    selector_config: SelectionConfig | None = None,
) -> Path:
    """Encode a full image using the DCT-aware path with AI coefficient selection."""
    if not image or not image[0]:
        raise ValueError("image cannot be empty")

    width = len(image[0])
    height = len(image)
    if any(len(row) != width for row in image):
        raise ValueError("image rows must have equal width")

    payload = bytearray(write_header(width=width, height=height, block_size=8))

    for block in split_image_into_blocks(image, block_size=8):
        payload.extend(
            encode_block_dct(
                block,
                keep_coeffs=keep_coeffs,
                strategy=strategy,
                quant_table=quant_table,
                selector_config=selector_config,
            )
        )

    path = Path(output_path)
    path.write_bytes(payload)
    return path


def decode_dct_archive(
    archive_path: str | Path,
    quant_table: str = "default",
) -> list[list[int]]:
    """Decode a DCT-coefficient J650 archive back to pixel values.

    This is the Python-side decoder for archives produced by
    ``encode_image_dct``.  It performs dequantization + IDCT per block.
    """
    from fileformat import HEADER_SIZE, read_header

    table = get_quantization_table(quant_table)

    data = Path(archive_path).read_bytes()
    header = read_header(data)
    width = int(header["width"])
    height = int(header["height"])

    payload = data[HEADER_SIZE:]
    image: list[list[int]] = [[0 for _ in range(width)] for _ in range(height)]

    blocks_per_row = (width + 7) // 8
    offset = 0
    block_index = 0

    while offset < len(payload):
        block_row = (block_index // blocks_per_row) * 8
        block_col = (block_index % blocks_per_row) * 8

        if payload[offset] == 0xFF:
            offset += 1
            block_index += 1
            continue

        if offset + 2 > len(payload):
            break

        length = payload[offset + 1]
        if offset + 2 + length > len(payload):
            break

        data_bytes = payload[offset + 2 : offset + 2 + length]
        offset += 2 + length

        coeff_indices: list[int] = []
        coeff_values: list[int] = []

        if data_bytes and data_bytes[0] == 0x02:
            pairs = data_bytes[1:]
            for pair_idx in range(0, len(pairs) - 1, 2):
                coeff_indices.append(pairs[pair_idx] & 0x3F)
                signed = pairs[pair_idx + 1]
                if signed > 127:
                    signed -= 256
                coeff_values.append(signed)
        else:
            block_index += 1
            continue

        coeffs = [0] * 64
        for ci, cv in zip(coeff_indices, coeff_values):
            coeffs[zigzag_indices[ci]] = cv

        coeff_matrix = [[coeffs[y * 8 + x] for x in range(8)] for y in range(8)]
        dequantized = dequantize_block_with_table(coeff_matrix, table)
        reconstructed = inverse_dct_2d([[float(v) for v in row] for row in dequantized])

        for row in range(8):
            for col in range(8):
                py = block_row + row
                px = block_col + col
                if py >= height or px >= width:
                    continue
                image[py][px] = max(0, min(3, int(round(reconstructed[row][col]))))

        block_index += 1

    return image
