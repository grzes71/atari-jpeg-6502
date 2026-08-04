from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from skimage.metrics import structural_similarity as _ssim


def psnr(original: Sequence[Sequence[int]], reconstructed: Sequence[Sequence[int]], max_value: float = 255.0) -> float:
    """Compute Peak Signal-to-Noise Ratio between two 2-D images.

    Values are cast to float64 before computing.  If the images are
    identical the function returns ``float('inf')``.
    """
    orig = np.asarray(original, dtype=np.float64)
    recon = np.asarray(reconstructed, dtype=np.float64)

    if orig.shape != recon.shape:
        raise ValueError(f"shape mismatch: {orig.shape} vs {recon.shape}")

    mse = np.mean((orig - recon) ** 2)
    if mse == 0:
        return float("inf")

    return float(20 * math.log10(max_value / math.sqrt(mse)))


def ssim(original: Sequence[Sequence[int]], reconstructed: Sequence[Sequence[int]], data_range: float = 255.0) -> float:
    """Compute Structural Similarity Index (SSIM) between two 2-D images."""

    orig = np.asarray(original, dtype=np.float64)
    recon = np.asarray(reconstructed, dtype=np.float64)

    if orig.shape != recon.shape:
        raise ValueError(f"shape mismatch: {orig.shape} vs {recon.shape}")

    win_size = 7 if min(len(orig), len(orig[0]) if orig.ndim == 2 else len(orig)) >= 7 else 3

    return float(
        _ssim(
            orig,
            recon,
            data_range=data_range,
            win_size=win_size,
            channel_axis=None,
        )
    )


def compute_all_metrics(
    original: Sequence[Sequence[int]],
    reconstructed: Sequence[Sequence[int]],
    max_value: float = 255.0,
) -> dict[str, float]:
    """Return PSNR and SSIM for the given image pair."""
    return {
        "psnr": psnr(original, reconstructed, max_value),
        "ssim": ssim(original, reconstructed, max_value),
    }
