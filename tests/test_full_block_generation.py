from dc_block import DCBlock
from mads_generator import generate_decoder_source, write_decoder_source
from build_mads import build_with_mads


def test_full_block_generation_contains_many_loads():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = generate_decoder_source(block)
    assert source.count("LDA #$") >= 10


def test_full_block_generation_builds_with_mads():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    path = write_decoder_source("out_decoder.asm", dc_value=block)
    result = build_with_mads("out_decoder.asm", dc_value=block)
    assert result.returncode == 0
