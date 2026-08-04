from dc_block import DCBlock, make_dc_block


def test_dc_block_contains_64_values():
    block = make_dc_block(3)
    assert len(block.values) == 64
    assert block.values[0] == 3
    assert block.values[-1] == 3


def test_dc_block_to_6502_words():
    block = DCBlock(values=tuple([2] * 64))
    assert block.to_6502_words() == [2] * 64
