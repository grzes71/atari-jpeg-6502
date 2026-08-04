from dc_block import DCBlock
from block_to_6502 import block_to_instruction_plan


def test_block_to_instruction_plan_returns_64_ops():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    plan = block_to_instruction_plan(block)
    assert len(plan) == 64
    assert plan[0] == ("load", 1)
    assert plan[-1] == ("load", 8)
