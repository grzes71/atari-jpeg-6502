from __future__ import annotations

import pytest

from adaptive_quantization import (
    AGGRESSIVE_QUANT,
    BALANCED_QUANT,
    FINE_QUANT,
    get_quantization_table,
    list_tables,
)


class TestGetQuantizationTable:
    def test_default_returns_balanced(self) -> None:
        assert get_quantization_table("default") == BALANCED_QUANT

    def test_aggressive_is_valid(self) -> None:
        t = get_quantization_table("aggressive")
        assert len(t) == 8
        assert all(len(row) == 8 for row in t)

    def test_balanced_is_valid(self) -> None:
        t = get_quantization_table("balanced")
        assert len(t) == 8
        assert all(len(row) == 8 for row in t)

    def test_fine_is_valid(self) -> None:
        t = get_quantization_table("fine")
        assert len(t) == 8
        assert all(len(row) == 8 for row in t)

    def test_single_char_aliases(self) -> None:
        assert get_quantization_table("a") == AGGRESSIVE_QUANT
        assert get_quantization_table("b") == BALANCED_QUANT
        assert get_quantization_table("f") == FINE_QUANT

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            get_quantization_table("nonexistent")

    def test_returns_copy_not_reference(self) -> None:
        a = get_quantization_table("default")
        b = get_quantization_table("default")
        a[0][0] = 999
        assert b[0][0] != 999

    def test_all_entries_positive(self) -> None:
        for name in list_tables():
            t = get_quantization_table(name)
            for row in t:
                assert all(v > 0 for v in row), f"table {name} has non-positive entry"


class TestListTables:
    def test_includes_all_tables(self) -> None:
        tables = list_tables()
        assert "aggressive" in tables
        assert "balanced" in tables
        assert "fine" in tables
        assert "lossless" in tables
        assert "default" in tables
