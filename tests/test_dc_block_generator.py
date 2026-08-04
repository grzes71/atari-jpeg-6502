from dc_block import DCBlock
from mads_generator import generate_decoder_source


def test_generator_emits_block_loop_for_dc_block():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = generate_decoder_source(block)
    assert "LDY #$00" in source
    assert "CPX #$40" in source
    assert "STA $E000,X" in source
