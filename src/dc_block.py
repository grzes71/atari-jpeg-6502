from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DCBlock:
    values: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.values) != 64:
            raise ValueError("DCBlock must contain exactly 64 values")

    @classmethod
    def from_scalar(cls, value: int) -> "DCBlock":
        return cls(values=tuple([value] * 64))

    @classmethod
    def from_rows(cls, rows: tuple[tuple[int, ...], ...]) -> "DCBlock":
        if len(rows) != 8:
            raise ValueError("DCBlock requires 8 rows")
        flat = [item for row in rows for item in row]
        if len(flat) != 64:
            raise ValueError("DCBlock requires 64 items")
        return cls(values=tuple(flat))

    def to_6502_words(self) -> list[int]:
        return list(self.values)


def make_dc_block(value: int) -> DCBlock:
    return DCBlock.from_scalar(value)
