from __future__ import annotations

import pytest

from ai_selector import (
    CoefficientSelection,
    SelectionConfig,
    _adaptive_keep_count,
    _score_coefficients,
    select_coefficients,
    select_coefficients_hybrid,
    select_coefficients_magnitude,
    select_coefficients_zigzag,
)


def _uniform_block(value: int = 1) -> list[list[int]]:
    return [[value] * 8 for _ in range(8)]


def _gradient_block() -> list[list[int]]:
    return [[(x + y) % 4 for x in range(8)] for y in range(8)]


# ---------------------------------------------------------------------------
# Zigzag selector
# ---------------------------------------------------------------------------

class TestZigzagSelector:
    def test_keeps_exact_count(self) -> None:
        sel = select_coefficients_zigzag(_gradient_block(), keep=5)
        assert sel.keep_count == 5
        assert len(sel.selected_indices) == 5
        assert len(sel.selected_values) == 5

    def test_dc_is_first(self) -> None:
        sel = select_coefficients_zigzag(_gradient_block(), keep=1)
        assert sel.selected_indices[0] == 0

    def test_clamps_to_64(self) -> None:
        sel = select_coefficients_zigzag(_gradient_block(), keep=100)
        assert sel.keep_count == 100
        assert len(sel.selected_indices) == 64


# ---------------------------------------------------------------------------
# Magnitude selector
# ---------------------------------------------------------------------------

class TestMagnitudeSelector:
    def test_keeps_exact_count(self) -> None:
        sel = select_coefficients_magnitude(_gradient_block(), keep=5)
        assert sel.keep_count == 5
        assert len(sel.selected_indices) == 5

    def test_indices_are_sorted(self) -> None:
        sel = select_coefficients_magnitude(_gradient_block(), keep=10)
        assert sel.selected_indices == sorted(sel.selected_indices)


# ---------------------------------------------------------------------------
# Hybrid selector
# ---------------------------------------------------------------------------

class TestHybridSelector:
    def test_dc_always_kept(self) -> None:
        sel = select_coefficients_hybrid(_gradient_block(), SelectionConfig(min_keep=1, max_keep=1))
        assert 0 in sel.selected_indices

    def test_respects_min_keep(self) -> None:
        sel = select_coefficients_hybrid(_gradient_block(), SelectionConfig(min_keep=8, max_keep=8))
        assert len(sel.selected_indices) == 8

    def test_adaptive_selects_between_min_and_max(self) -> None:
        sel = select_coefficients_hybrid(_gradient_block(), SelectionConfig(min_keep=1, max_keep=64))
        assert 1 <= sel.keep_count <= 64

    def test_uniform_block_produces_minimal_selection(self) -> None:
        sel = select_coefficients_hybrid(_uniform_block(5), SelectionConfig(min_keep=2, max_keep=64))
        assert sel.keep_count >= 2


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

class TestSelectCoefficients:
    def test_dispatches_to_zigzag(self) -> None:
        sel = select_coefficients(_gradient_block(), strategy="zigzag", keep=3)
        assert sel.ordering == "zigzag"
        assert sel.keep_count == 3

    def test_dispatches_to_magnitude(self) -> None:
        sel = select_coefficients(_gradient_block(), strategy="magnitude", keep=3)
        assert sel.ordering == "magnitude"

    def test_dispatches_to_hybrid(self) -> None:
        sel = select_coefficients(_gradient_block(), strategy="hybrid")
        assert sel.ordering == "hybrid"

    def test_rejects_unknown_strategy(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            select_coefficients(_gradient_block(), strategy="nonexistent")


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

class TestScoring:
    def test_dc_always_gets_inf_score(self) -> None:
        scores = _score_coefficients(_gradient_block(), SelectionConfig())
        dc_scores = [s for idx, s in scores if idx == 0]
        assert len(dc_scores) == 1
        assert dc_scores[0] == float("inf")

    def test_respects_threshold(self) -> None:
        scores = _score_coefficients(_gradient_block(), SelectionConfig(magnitude_threshold=999999))
        assert len(scores) == 1  # DC only (inf passes threshold)


# ---------------------------------------------------------------------------
# Adaptive keep count
# ---------------------------------------------------------------------------

class TestAdaptiveKeepCount:
    def test_empty_returns_zero(self) -> None:
        assert _adaptive_keep_count([], SelectionConfig()) == 0

    def test_only_dc_returns_one(self) -> None:
        dc_only = [(0, float("inf"))]
        assert _adaptive_keep_count(dc_only, SelectionConfig()) == 1

    def test_clamps_to_max_keep(self) -> None:
        many = [(0, float("inf"))] + [(i, 100.0) for i in range(1, 64)]
        result = _adaptive_keep_count(many, SelectionConfig(max_keep=5))
        assert result <= 5
