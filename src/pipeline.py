from __future__ import annotations

from pathlib import Path

from block_utils import split_image_into_blocks
from build_mads import export_xex
from dc_block import DCBlock
from decoder_model import build_block_decoder_source
from dct import forward_dct_2d, reconstruct_block_from_coefficients
from encoder import encode_image
from image_io import load_binary_image_2bpp
from png_export import decompress, screen_to_png
from quantization import quantize_block
from zigzag import coefficients_to_block_values, zigzag_extract


def build_pipeline_example(input_path: str | Path, width: int, height: int, output_asm: str | Path = "decoder6502.asm", keep_coeffs: int = 10) -> tuple[list[list[int]], list[DCBlock], Path]:
    image = load_binary_image_2bpp(input_path, width=width, height=height)

    block_models: list[DCBlock] = []
    for block_rows in split_image_into_blocks(image, block_size=8):
        coeffs = zigzag_extract(quantize_block([[int(value) for value in row] for row in forward_dct_2d(block_rows)]), keep=keep_coeffs)
        reconstruction = reconstruct_block_from_coefficients(coeffs, keep=keep_coeffs)
        block_models.append(DCBlock.from_rows(tuple(tuple(row) for row in reconstruction)))

    asm_path = Path(output_asm)
    asm_source = build_block_decoder_source(block_models[:3], block_count=len(block_models[:3]))
    asm_path.write_text(asm_source, encoding="utf-8")
    return image, block_models, asm_path


def run_full_pipeline(
    input_path: str | Path,
    width: int,
    height: int,
    output_bin: str | Path = "output.j650",
    output_asm: str | Path = "decoder6502.asm",
    output_xex: str | Path | None = None,
    antic_mode: str = "E",
    palette: tuple[int, ...] | list[int] | None = None,
    keep_coeffs: int = 10,
    export_png: str | Path | None = None,
    scale: int = 2,
) -> tuple[list[list[int]], list[DCBlock], Path, Path]:
    image = load_binary_image_2bpp(input_path, width=width, height=height)
    blocks: list[DCBlock] = []
    for block_rows in split_image_into_blocks(image, block_size=8):
        coeffs = zigzag_extract(quantize_block([[int(value) for value in row] for row in forward_dct_2d(block_rows)]), keep=keep_coeffs)
        reconstruction = reconstruct_block_from_coefficients(coeffs, keep=keep_coeffs)
        blocks.append(DCBlock.from_rows(tuple(tuple(row) for row in reconstruction)))

    bin_path = encode_image(image, output_bin, keep_coeffs=keep_coeffs)
    asm_path = Path(output_asm)
    asm_source = build_block_decoder_source(blocks[:3], block_count=len(blocks[:3]))
    asm_path.write_text(asm_source, encoding="utf-8")

    xex_path = None
    if output_xex is not None:
        xex_path = export_xex(asm_path, output_xex, antic_mode=antic_mode, palette=palette)

    if export_png is not None:
        screen_bytes = decompress(bin_path.read_bytes(), antic_mode=antic_mode)
        screen_to_png(screen_bytes, mode=antic_mode, palette_colors=palette, output_path=export_png, scale=scale)

    return image, blocks, bin_path, asm_path
