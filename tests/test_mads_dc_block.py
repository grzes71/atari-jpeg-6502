from pathlib import Path

from mads_generator import generate_decoder_source, write_decoder_source


def test_generate_decoder_source_contains_full_dc_block_stub():
    source = generate_decoder_source()
    assert "ORG $C000" in source
    assert "LDA #$01" in source
    assert "LDA #$03" in source
    assert "LDA #$FF" in source
    assert "STA $E000,X" in source
    assert "RTS" in source


def test_generate_decoder_source_uses_provided_dc_value():
    source = generate_decoder_source(dc_value=2)
    assert "LDA #$02" in source


def test_write_decoder_source_creates_file():
    path = write_decoder_source(Path("out_decoder.asm"))
    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("; RLE-based")
