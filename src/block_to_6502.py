from __future__ import annotations

from dc_block import DCBlock


def block_to_instruction_plan(block: DCBlock) -> list[tuple[str, int]]:
    return [("load", value) for value in block.values[:64]]
