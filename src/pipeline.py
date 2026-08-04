from __future__ import annotations

from pathlib import Path

from adaptive_quantization import get_quantization_table
from ai_selector import SelectionConfig, select_coefficients
from block_utils import split_image_into_blocks
from build_mads import export_xex
from dc_block import DCBlock
from decompressor_6502 import generate_example_asm
from decoder_model import build_block_decoder_source
from dct import forward_dct_2d, inverse_dct_2d, reconstruct_block_from_coefficients
from encoder import encode_block_dct, encode_image, encode_image_dct
from image_io import load_binary_image_2bpp
from metrics import compute_all_metrics
from png_export import decompress, screen_to_png
from quantization import dequantize_block, quantize_block
from zigzag import coefficients_to_block_values, zigzag_extract, zigzag_indices


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
    generate_example_asm(
        j650_bin_path=str(bin_path),
        output_asm_path=str(asm_path),
        antic_mode=antic_mode,
        palette=tuple(palette) if palette else (0x00, 0x02, 0x08, 0x0E),
    )

    xex_path = None
    if output_xex is not None:
        xex_path = export_xex(asm_path, output_xex, antic_mode=antic_mode, palette=palette)

    if export_png is not None:
        screen_bytes = decompress(bin_path.read_bytes(), antic_mode=antic_mode)
        screen_to_png(screen_bytes, mode=antic_mode, palette_colors=palette, output_path=export_png, scale=scale)

    return image, blocks, bin_path, asm_path


def run_ai_pipeline(
    input_path: str | Path,
    width: int,
    height: int,
    output_bin: str | Path = "output_ai.j650",
    output_asm: str | Path = "decoder6502.asm",
    output_xex: str | Path | None = None,
    antic_mode: str = "E",
    palette: tuple[int, ...] | list[int] | None = None,
    keep_coeffs: int = 10,
    strategy: str = "hybrid",
    quant_table: str = "default",
    selector_config: SelectionConfig | None = None,
    mode: str = "pixel",
    export_png: str | Path | None = None,
    scale: int = 2,
) -> dict:
    """Run the AI-assisted DCT-aware encoding pipeline.

    *mode*: ``"pixel"`` (default) — reconstruct pixels from selected
    coefficients, 6502-decoder compatible.  ``"coefficients"`` — store
    sparse DCT coefficients (needs DCT-capable decoder).

    Returns a dict with ``image``, ``blocks``, ``bin_path``, ``asm_path``.
    """
    image = load_binary_image_2bpp(input_path, width=width, height=height)

    bin_path = encode_image_dct(
        image,
        output_bin,
        keep_coeffs=keep_coeffs,
        strategy=strategy,
        quant_table=quant_table,
        selector_config=selector_config,
        mode=mode,
    )

    blocks: list[DCBlock] = []
    for block_rows in split_image_into_blocks(image, block_size=8):
        coeffs = zigzag_extract(
            quantize_block([[int(value) for value in row] for row in forward_dct_2d(block_rows)]),
            keep=keep_coeffs,
        )
        reconstruction = reconstruct_block_from_coefficients(coeffs, keep=keep_coeffs)
        blocks.append(DCBlock.from_rows(tuple(tuple(row) for row in reconstruction)))

    asm_path = Path(output_asm)
    generate_example_asm(
        j650_bin_path=str(bin_path),
        output_asm_path=str(asm_path),
        antic_mode=antic_mode,
        palette=tuple(palette) if palette else (0x00, 0x02, 0x08, 0x0E),
    )

    if output_xex is not None:
        export_xex(asm_path, output_xex, antic_mode=antic_mode, palette=palette)

    result: dict = {
        "image": image,
        "blocks": blocks,
        "bin_path": bin_path,
        "asm_path": asm_path,
    }

    if export_png is not None:
        screen_bytes = decompress(bin_path.read_bytes(), antic_mode=antic_mode)
        screen_to_png(screen_bytes, mode=antic_mode, palette_colors=palette, output_path=export_png, scale=scale)

    file_size = bin_path.stat().st_size if bin_path.exists() else 0
    result["file_size_bytes"] = file_size

    return result


def run_experiment(
    input_path: str | Path,
    width: int,
    height: int,
    keep_coeffs: int = 10,
    strategy: str = "hybrid",
    quant_table: str = "default",
    selector_config: SelectionConfig | None = None,
    mode: str = "pixel",
) -> dict:
    """Run a single experiment: encode + decode + measure quality.

    *mode*: ``"pixel"`` decodes via standard J650 pixel path (6502 compatible).
    ``"coefficients"`` decodes via DCT dequantization + IDCT.

    Returns a dict with PSNR, SSIM, file size, coefficient count, and
    compression time.
    """
    import tempfile
    import time

    image = load_binary_image_2bpp(input_path, width=width, height=height)

    with tempfile.NamedTemporaryFile(suffix=".j650", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        start = time.perf_counter()
        encode_image_dct(
            image,
            tmp_path,
            keep_coeffs=keep_coeffs,
            strategy=strategy,
            quant_table=quant_table,
            selector_config=selector_config,
            mode=mode,
        )
        elapsed = time.perf_counter() - start

        if mode == "coefficients":
            from encoder import decode_dct_archive

            reconstructed = decode_dct_archive(tmp_path, quant_table=quant_table)
        else:
            from decode_simple import decode_simple_j650

            reconstructed = decode_simple_j650(tmp_path)

        # Scale 0..3 pixel values to 0..255 for meaningful PSNR/SSIM
        orig_scaled = [[p * 85 for p in row] for row in image]
        recon_scaled = [[p * 85 for p in row] for row in reconstructed]

        metrics = compute_all_metrics(orig_scaled, recon_scaled, max_value=255.0)

        file_size = tmp_path.stat().st_size

        total_coeffs = 0
        data = tmp_path.read_bytes()
        from fileformat import HEADER_SIZE, read_header

        header = read_header(data)
        payload = data[HEADER_SIZE:]
        offset = 0
        while offset < len(payload):
            if payload[offset] == 0xFF:
                offset += 1
                continue
            if offset + 2 > len(payload):
                break
            length = payload[offset + 1]
            if offset + 2 + length > len(payload):
                break
            block_data = payload[offset + 2 : offset + 2 + length]
            if block_data and block_data[0] == 0x02:
                total_coeffs += (len(block_data) - 1) // 2
            offset += 2 + length

        return {
            "psnr": metrics["psnr"],
            "ssim": metrics["ssim"],
            "file_size_bytes": file_size,
            "total_coefficients": total_coeffs,
            "compression_time_s": elapsed,
            "strategy": strategy,
            "quant_table": quant_table,
            "keep_coeffs": keep_coeffs,
            "mode": mode,
        }
    finally:
        tmp_path.unlink(missing_ok=True)
