from __future__ import annotations

from copy import deepcopy
from typing import Sequence

# ---------------------------------------------------------------------------
# Atari-optimised quantisation tables
#
# These are scaled for 2-bpp (0..3) pixel values.  JPEG tables are designed
# for 8-bit (0..255) content; dividing by ~64 produces appropriate divisors
# for the Atari palette range.
#
# Each table is also taken through max(1, divisor) so that a "lossless"
# table (all 1s) preserves every coefficient.
# ---------------------------------------------------------------------------

def _scale_table(source: list[list[int]], divisor: int) -> list[list[int]]:
    """Scale a JPEG-style table down for 2-bpp content."""
    return [[max(1, v // divisor) for v in row] for row in source]

# Base tables (scaled from JPEG luminance defaults)
_AGGRESSIVE_BASE: list[list[int]] = [
    [24, 18, 15, 24, 36, 60, 76, 92],
    [18, 18, 21, 28, 39, 87, 90, 82],
    [21, 20, 24, 36, 60, 86, 104, 84],
    [21, 26, 33, 44, 76, 130, 120, 93],
    [27, 33, 56, 84, 102, 164, 154, 116],
    [36, 52, 82, 96, 122, 156, 170, 138],
    [74, 96, 117, 130, 154, 182, 180, 152],
    [108, 138, 142, 147, 168, 150, 154, 148],
]

# Aggressive – higher compression, more loss  (÷32)
AGGRESSIVE_QUANT: list[list[int]] = _scale_table(_AGGRESSIVE_BASE, 32)

# Balanced – moderate compression  (÷16)
BALANCED_QUANT: list[list[int]] = _scale_table(_AGGRESSIVE_BASE, 16)

# Fine – higher quality  (÷8)
FINE_QUANT: list[list[int]] = _scale_table(_AGGRESSIVE_BASE, 8)

# Lossless – preserve all DCT coefficients (identity)
LOSSLESS_QUANT: list[list[int]] = [[1] * 8 for _ in range(8)]

_TABLES: dict[str, list[list[int]]] = {
    "default": deepcopy(BALANCED_QUANT),
    "aggressive": deepcopy(AGGRESSIVE_QUANT),
    "balanced": deepcopy(BALANCED_QUANT),
    "fine": deepcopy(FINE_QUANT),
    "lossless": deepcopy(LOSSLESS_QUANT),
}

# Single-character aliases for CLI convenience
_ALIASES: dict[str, str] = {"a": "aggressive", "b": "balanced", "f": "fine", "l": "lossless"}


def get_quantization_table(name: str = "default") -> list[list[int]]:
    """Return a named 8×8 quantization table.

    Recognised names: ``default``, ``aggressive``, ``balanced``, ``fine``.
    Single-letter aliases ``a``, ``b``, ``f`` are also accepted.
    """
    resolved = _ALIASES.get(name, name)
    table = _TABLES.get(resolved)
    if table is None:
        raise ValueError(f"unknown quantization table: {name!r}")
    return deepcopy(table)


def list_tables() -> list[str]:
    """Return the list of available table names (full names only)."""
    return sorted(_TABLES.keys())
