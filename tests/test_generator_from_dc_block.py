from dc_block import make_dc_block
from mads_generator import generate_decoder_source


def test_generator_accepts_dc_block():
    block = make_dc_block(5)
    source = generate_decoder_source(block)
    assert "LDA #$05" in source
