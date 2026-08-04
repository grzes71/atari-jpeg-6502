from __future__ import annotations

from pathlib import Path
from typing import Sequence

from adaptive_quantization import get_quantization_table
from ai_selector import SelectionConfig, select_coefficients
from block_utils import split_image_into_blocks
from dct import forward_dct_2d, inverse_dct_2d, reconstruct_block_from_coefficients
from fileformat import HEADER_SIZE, build_simple_block_payload, build_sparse_coefficient_payload, write_block, write_header
from quantization import dequantize_block, dequantize_block_with_table, quantize_block, quantize_block_with_table
from rle import encode_rle
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
    mode: str = "coefficients",
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
    mode:
        ``"coefficients"`` — store sparse (index, value) DCT coefficients
        (needs DCT-capable decoder).  ``"pixel"`` — reconstruct pixels from
        selected coefficients and store in packed 16-byte format (6502
        decoder compatible).
    """
    if mode == "pixel":
        return _encode_block_dct_pixel(
            block,
            keep_coeffs=keep_coeffs,
            strategy=strategy,
            quant_table=quant_table,
            selector_config=selector_config,
        )

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


def _encode_block_dct_pixel(
    block: list[list[int]],
    keep_coeffs: int = 10,
    strategy: str = "hybrid",
    quant_table: str = "default",
    selector_config: SelectionConfig | None = None,
) -> bytes:
    """AI-assisted DCT encoding → reconstruct pixels → packed 16-byte format.

    This is the hybrid path: the AI selects coefficients in the DCT domain,
    but the output is plain pixel values compatible with the 6502 decoder.

    Pixel values are scaled 0..3 → 0..255 before DCT so that the standard
    JPEG quantization tables operate in their designed range, then scaled
    back after IDCT.
    """
    table = get_quantization_table(quant_table)

    # Scale 0..3 pixels to 0..255 for proper DCT dynamic range,
    # then level-shift by -128 (standard JPEG centering)
    scaled_block = [[p * 85 - 128 for p in row] for row in block]

    dct_coeffs = forward_dct_2d(scaled_block)
    dct_rounded = [[int(round(v)) for v in row] for row in dct_coeffs]

    # Direct integer quantisation (no Q8.8 clipping — DCT coeffs can
    # exceed [-128,127] for 0..255 content even after level shift)
    q_block: list[list[int]] = []
    for row_idx in range(8):
        q_row: list[int] = []
        for col_idx in range(8):
            divisor = max(1, table[row_idx][col_idx])
            q_row.append(int(round(dct_rounded[row_idx][col_idx] / divisor)))
        q_block.append(q_row)

    selection = select_coefficients(
        q_block,
        strategy=strategy,
        keep=keep_coeffs,
        config=selector_config,
    )

    # Reconstruct coefficient matrix (only selected coefficients, rest zero)
    coeffs = [0] * 64
    for zz_idx, value in zip(selection.selected_indices, selection.selected_values):
        coeffs[zigzag_indices[zz_idx]] = value

    # Direct integer dequantisation
    coeff_matrix = [[0 for _ in range(8)] for _ in range(8)]
    for y in range(8):
        for x in range(8):
            coeff_matrix[y][x] = coeffs[y * 8 + x] * table[y][x]

    pixels = inverse_dct_2d([[float(v) for v in row] for row in coeff_matrix])

    # Scale back: reverse level shift +128, then 0..255 → 0..3
    flat_pixels = [
        max(0, min(3, int(round((pixels[row][col] + 128) / 85.0))))
        for row in range(8)
        for col in range(8)
    ]

    if all(p == 0 for p in flat_pixels):
        return b"\xff"

    # ----- Build candidate encodings (all 6502-decoder compatible) -----

    # Packed: 16 bytes (always 18 total)
    packed = bytearray(16)
    for index, value in enumerate(flat_pixels):
        byte_index = index // 4
        bit_offset = (index % 4) * 2
        packed[byte_index] |= (value & 0x03) << bit_offset
    packed_payload = bytes([0x01, 16]) + bytes(packed)

    # Sparse: (index, value) pairs — good when few pixels differ from zero
    nonzero_pairs = [(i, v) for i, v in enumerate(flat_pixels) if v != 0]
    if nonzero_pairs:
        sparse_inner = bytearray([0x02])
        for idx, val in nonzero_pairs:
            sparse_inner.append(idx & 0x3F)
            sparse_inner.append(val & 0x03)
        sparse_payload = bytes([0x01, len(sparse_inner)]) + bytes(sparse_inner)
    else:
        sparse_payload = None

    # RLE: (count, value) runs — great for uniform or striped blocks
    rle_inner = bytearray([0x03])
    rle_inner.extend(encode_rle(flat_pixels))
    rle_payload = bytes([0x01, len(rle_inner)]) + bytes(rle_inner)

    # Pick the smallest
    best = packed_payload
    if sparse_payload is not None and len(sparse_payload) < len(best):
        best = sparse_payload
    if len(rle_payload) < len(best):
        best = rle_payload

    return write_block(best)


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
    mode: str = "coefficients",
) -> Path:
    """Encode a full image using the DCT-aware path with AI coefficient selection.

    *mode* can be ``"coefficients"`` (sparse DCT payload) or ``"pixel"``
    (reconstruct pixels → packed 16-byte, 6502-decoder compatible).
    """
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
                mode=mode,
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
