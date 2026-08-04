from __future__ import annotations

from copy import deepcopy
from typing import Sequence

# ---------------------------------------------------------------------------
# Atari-optimised quantisation tables
#
# These are derived from the standard JPEG luminance table but scaled to be
# more aggressive for Atari-style 2-bpp imagery where reconstruction errors
# are less visible because of the limited palette.
# ---------------------------------------------------------------------------

# Aggressive table – higher compression, more loss
AGGRESSIVE_QUANT: list[list[int]] = [
    [24, 18, 15, 24, 36, 60, 76, 92],
    [18, 18, 21, 28, 39, 87, 90, 82],
    [21, 20, 24, 36, 60, 86, 104, 84],
    [21, 26, 33, 44, 76, 130, 120, 93],
    [27, 33, 56, 84, 102, 164, 154, 116],
    [36, 52, 82, 96, 122, 156, 170, 138],
    [74, 96, 117, 130, 154, 182, 180, 152],
    [108, 138, 142, 147, 168, 150, 154, 148],
]

# Balanced table – moderate compression
BALANCED_QUANT: list[list[int]] = [
    [18, 13, 12, 18, 27, 45, 57, 69],
    [13, 13, 15, 21, 29, 65, 67, 62],
    [15, 15, 18, 27, 45, 64, 77, 63],
    [15, 19, 24, 33, 57, 97, 90, 70],
    [20, 24, 41, 63, 76, 122, 115, 87],
    [27, 39, 61, 72, 91, 117, 127, 103],
    [55, 72, 87, 97, 115, 136, 135, 113],
    [81, 103, 106, 110, 126, 112, 115, 111],
]

# Fine table – higher quality
FINE_QUANT: list[list[int]] = [
    [12, 8, 8, 12, 18, 30, 38, 46],
    [9, 9, 10, 14, 19, 43, 45, 41],
    [10, 10, 12, 18, 30, 43, 51, 42],
    [10, 13, 16, 22, 38, 65, 60, 46],
    [14, 16, 28, 42, 51, 82, 77, 58],
    [18, 26, 41, 48, 60, 78, 85, 69],
    [37, 48, 58, 65, 77, 90, 90, 76],
    [54, 69, 71, 73, 84, 75, 77, 74],
]

_TABLES: dict[str, list[list[int]]] = {
    "default": deepcopy(AGGRESSIVE_QUANT),
    "aggressive": deepcopy(AGGRESSIVE_QUANT),
    "balanced": deepcopy(BALANCED_QUANT),
    "fine": deepcopy(FINE_QUANT),
}

# Single-character aliases for CLI convenience
_ALIASES: dict[str, str] = {"a": "aggressive", "b": "balanced", "f": "fine"}


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
