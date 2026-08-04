"""Experiment runner for v1.0.0 AI-Assisted Encoder.

Usage:
    python -m experiments.runner samples/myimage.bin --width 160 --height 192
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _run_experiments(
    input_path: Path,
    width: int,
    height: int,
) -> list[dict[str, Any]]:
    from pipeline import run_experiment

    configs = [
        # Baseline: classic zigzag at various keep levels
        {"label": "zigzag-k4", "strategy": "zigzag", "keep_coeffs": 4, "quant_table": "default"},
        {"label": "zigzag-k8", "strategy": "zigzag", "keep_coeffs": 8, "quant_table": "default"},
        {"label": "zigzag-k12", "strategy": "zigzag", "keep_coeffs": 12, "quant_table": "default"},
        {"label": "zigzag-k16", "strategy": "zigzag", "keep_coeffs": 16, "quant_table": "default"},
        # Magnitude-first at various keep levels
        {"label": "mag-k4", "strategy": "magnitude", "keep_coeffs": 4, "quant_table": "default"},
        {"label": "mag-k8", "strategy": "magnitude", "keep_coeffs": 8, "quant_table": "default"},
        {"label": "mag-k12", "strategy": "magnitude", "keep_coeffs": 12, "quant_table": "default"},
        {"label": "mag-k16", "strategy": "magnitude", "keep_coeffs": 16, "quant_table": "default"},
        # Hybrid (adaptive) with different quant tables
        {"label": "hybrid-default", "strategy": "hybrid", "keep_coeffs": 10, "quant_table": "default"},
        {"label": "hybrid-aggressive", "strategy": "hybrid", "keep_coeffs": 10, "quant_table": "aggressive"},
        {"label": "hybrid-balanced", "strategy": "hybrid", "keep_coeffs": 10, "quant_table": "balanced"},
        {"label": "hybrid-fine", "strategy": "hybrid", "keep_coeffs": 10, "quant_table": "fine"},
    ]

    results: list[dict[str, Any]] = []
    for cfg in configs:
        print(f"  Running {cfg['label']} ...", end=" ", flush=True)
        result = run_experiment(
            input_path=input_path,
            width=width,
            height=height,
            keep_coeffs=cfg["keep_coeffs"],
            strategy=cfg["strategy"],
            quant_table=cfg["quant_table"],
        )
        result["label"] = cfg["label"]
        results.append(result)
        print(
            f"PSNR={result['psnr']:.2f}  SSIM={result['ssim']:.4f}  "
            f"size={result['file_size_bytes']}B  coeffs={result['total_coefficients']}  "
            f"time={result['compression_time_s']:.3f}s"
        )

    return results


def _print_table(results: list[dict[str, Any]]) -> None:
    print()
    print(f"{'Label':<20} {'PSNR':>8} {'SSIM':>8} {'Size(B)':>8} {'Coeffs':>8} {'Time(s)':>8}")
    print("-" * 65)
    for r in results:
        print(
            f"{r['label']:<20} "
            f"{r['psnr']:>8.2f} "
            f"{r['ssim']:>8.4f} "
            f"{r['file_size_bytes']:>8} "
            f"{r['total_coefficients']:>8} "
            f"{r['compression_time_s']:>8.3f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v1.0.0 AI-Assisted Encoder experiments")
    parser.add_argument("input_path", help="Input binary image path (.bin)")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--output-json", help="Save results to JSON file")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    if not input_path.exists():
        raise SystemExit(f"input file not found: {input_path}")

    print(f"Running experiments on {input_path} ({args.width}x{args.height})")
    print()

    results = _run_experiments(input_path, args.width, args.height)

    _print_table(results)

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
