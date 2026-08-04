from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from zigzag import zigzag_indices


@dataclass
class CoefficientSelection:
    """Result of heuristic coefficient selection for one 8×8 block."""

    selected_indices: list[int]
    selected_values: list[int]
    ordering: str = "zigzag"
    keep_count: int = 64


@dataclass
class SelectionConfig:
    strategy: str = "hybrid"
    min_keep: int = 4
    max_keep: int = 64
    magnitude_threshold: float = 0.0
    position_weight_power: float = 1.0


# ---------------------------------------------------------------------------
# Position-importance weights  (JPEG-style: lower-frequency positions are
# more important).  Higher values → more likely to be kept.
# ---------------------------------------------------------------------------
_POSITION_WEIGHTS: list[float] = [
    1.0000, 0.8000, 0.6500, 0.5000, 0.4000, 0.3000, 0.2000, 0.1500,
    0.8000, 0.6500, 0.5500, 0.4500, 0.3500, 0.2500, 0.1800, 0.1200,
    0.6500, 0.5500, 0.4500, 0.3800, 0.3000, 0.2200, 0.1500, 0.1000,
    0.5000, 0.4500, 0.3800, 0.3200, 0.2500, 0.1800, 0.1200, 0.0800,
    0.4000, 0.3500, 0.3000, 0.2500, 0.2000, 0.1500, 0.1000, 0.0600,
    0.3000, 0.2500, 0.2200, 0.1800, 0.1500, 0.1000, 0.0700, 0.0500,
    0.2000, 0.1800, 0.1500, 0.1200, 0.1000, 0.0700, 0.0500, 0.0300,
    0.1500, 0.1200, 0.1000, 0.0800, 0.0600, 0.0500, 0.0300, 0.0200,
]


def _score_coefficients(
    quantized_block: Sequence[Sequence[int]],
    config: SelectionConfig,
) -> list[tuple[int, float]]:
    """Return ``(zigzag_index, score)`` pairs sorted by descending score."""
    scores: list[tuple[int, float]] = []
    for zz_idx, linear_idx in enumerate(zigzag_indices):
        row = linear_idx // 8
        col = linear_idx % 8
        magnitude = abs(quantized_block[row][col])

        weight = _POSITION_WEIGHTS[zz_idx] ** config.position_weight_power

        if zz_idx == 0:
            score = float("inf")
        else:
            score = float(magnitude) * weight

        if score < config.magnitude_threshold:
            continue

        scores.append((zz_idx, score))

    scores.sort(key=lambda item: item[1], reverse=True)
    return scores


def _adaptive_keep_count(
    scored: list[tuple[int, float]],
    config: SelectionConfig,
) -> int:
    """Decide how many coefficients to keep based on score distribution."""
    if not scored:
        return 0

    ac_scores = [s for idx, s in scored if idx != 0]
    if not ac_scores:
        return min(1, config.max_keep)

    mean_score = sum(ac_scores) / len(ac_scores)
    significant = sum(1 for s in ac_scores if s >= mean_score * 0.5)

    keep = 1 + significant
    return max(config.min_keep, min(config.max_keep, keep))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def select_coefficients_zigzag(
    quantized_block: Sequence[Sequence[int]],
    keep: int = 10,
) -> CoefficientSelection:
    """Classic ZigZag: preserve the first *keep* coefficients in scan order."""
    indices: list[int] = []
    values: list[int] = []
    for zz_idx in range(min(keep, 64)):
        linear_idx = zigzag_indices[zz_idx]
        row = linear_idx // 8
        col = linear_idx % 8
        indices.append(zz_idx)
        values.append(quantized_block[row][col])
    return CoefficientSelection(selected_indices=indices, selected_values=values, ordering="zigzag", keep_count=keep)


def select_coefficients_magnitude(
    quantized_block: Sequence[Sequence[int]],
    keep: int = 10,
) -> CoefficientSelection:
    """Magnitude-first: keep the *keep* largest-magnitude coefficients."""
    scored = _score_coefficients(quantized_block, SelectionConfig(strategy="magnitude", position_weight_power=0.0))
    top = scored[:keep]
    top.sort(key=lambda item: item[0])
    indices = [idx for idx, _ in top]
    values: list[int] = []
    for idx in indices:
        linear_idx = zigzag_indices[idx]
        values.append(quantized_block[linear_idx // 8][linear_idx % 8])
    return CoefficientSelection(selected_indices=indices, selected_values=values, ordering="magnitude", keep_count=len(indices))


def select_coefficients_hybrid(
    quantized_block: Sequence[Sequence[int]],
    config: SelectionConfig | None = None,
) -> CoefficientSelection:
    """Hybrid: DC always kept; AC selected by position-weighted magnitude.

    The number of kept coefficients is decided adaptively per block unless
    ``config.max_keep == config.min_keep``.
    """
    if config is None:
        config = SelectionConfig()

    scored = _score_coefficients(quantized_block, config)

    if config.max_keep == config.min_keep:
        keep = config.min_keep
    else:
        keep = _adaptive_keep_count(scored, config)

    top = scored[:keep]
    top.sort(key=lambda item: item[0])

    indices = [idx for idx, _ in top]
    values: list[int] = []
    for idx in indices:
        linear_idx = zigzag_indices[idx]
        values.append(quantized_block[linear_idx // 8][linear_idx % 8])
    return CoefficientSelection(selected_indices=indices, selected_values=values, ordering="hybrid", keep_count=len(indices))


# ---------------------------------------------------------------------------
# Convenience – pick a strategy by name
# ---------------------------------------------------------------------------

def select_coefficients(
    quantized_block: Sequence[Sequence[int]],
    strategy: str = "hybrid",
    keep: int = 10,
    config: SelectionConfig | None = None,
) -> CoefficientSelection:
    """Dispatch to the appropriate selector based on *strategy*."""
    if strategy == "zigzag":
        return select_coefficients_zigzag(quantized_block, keep=keep)
    if strategy == "magnitude":
        return select_coefficients_magnitude(quantized_block, keep=keep)
    if strategy == "hybrid":
        return select_coefficients_hybrid(quantized_block, config=config)
    raise ValueError(f"unknown coefficient selection strategy: {strategy!r}")
