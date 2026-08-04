from __future__ import annotations

import argparse
from pathlib import Path

from ai_selector import SelectionConfig
from pipeline import run_ai_pipeline, run_full_pipeline


def _parse_palette(value: str | None, antic_mode: str = "E") -> tuple[int, ...] | None:
    if value is None:
        return None
    parts = [part.strip() for part in value.split(",") if part.strip()]
    antic_mode = antic_mode.upper()

    if antic_mode == "F":
        if len(parts) != 2:
            raise SystemExit("palette must contain exactly 2 comma-separated values for ANTIC mode F")
    elif len(parts) not in {4, 5}:
        raise SystemExit("palette must contain 4 values for ANTIC modes D/E, or 5 values when including background")

    return tuple(int(part, 0) for part in parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a J650 archive, decoder assembly, and optional XEX preview")
    parser.add_argument("input_path", help="Input binary image path")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--output-bin", default="output.j650")
    parser.add_argument("--output-asm", default="decoder6502.asm")
    parser.add_argument("--output-xex")
    parser.add_argument("--export-png")
    parser.add_argument("--scale", type=int, choices=[1, 2, 4], default=2)
    parser.add_argument("--antic-mode", choices=["D", "E", "F"], default="E")
    parser.add_argument("--palette")
    parser.add_argument("--palette-rgb", dest="palette_rgb")
    parser.add_argument("--keep-coeffs", type=int, default=10, help="Number of zigzag coefficients preserved per 8x8 block (lower = smaller output, lower quality)")
    parser.add_argument("--ai", action="store_true", help="Use AI-assisted DCT-aware encoder (v1.0.0)")
    parser.add_argument("--strategy", choices=["zigzag", "magnitude", "hybrid"], default="hybrid", help="Coefficient selection strategy (only with --ai)")
    parser.add_argument("--quant-table", choices=["default", "aggressive", "balanced", "fine"], default="default", help="Quantization table (only with --ai)")
    parser.add_argument("--min-keep", type=int, default=4, help="Minimum coefficients per block (hybrid strategy)")
    parser.add_argument("--max-keep", type=int, default=64, help="Maximum coefficients per block (hybrid strategy)")
    args = parser.parse_args()

    palette_value = args.palette or args.palette_rgb

    if args.ai:
        config = SelectionConfig(
            strategy=args.strategy,
            min_keep=args.min_keep,
            max_keep=args.max_keep,
        )
        run_ai_pipeline(
            input_path=Path(args.input_path),
            width=args.width,
            height=args.height,
            output_bin=args.output_bin,
            output_asm=args.output_asm,
            output_xex=args.output_xex,
            antic_mode=args.antic_mode,
            palette=_parse_palette(palette_value, antic_mode=args.antic_mode),
            keep_coeffs=args.keep_coeffs,
            strategy=args.strategy,
            quant_table=args.quant_table,
            selector_config=config,
            export_png=args.export_png,
            scale=args.scale,
        )
    else:
        run_full_pipeline(
            input_path=Path(args.input_path),
            width=args.width,
            height=args.height,
            output_bin=args.output_bin,
            output_asm=args.output_asm,
            output_xex=args.output_xex,
            antic_mode=args.antic_mode,
            palette=_parse_palette(palette_value, antic_mode=args.antic_mode),
            keep_coeffs=args.keep_coeffs,
            export_png=args.export_png,
            scale=args.scale,
        )


if __name__ == "__main__":
    main()
