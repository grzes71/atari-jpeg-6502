from mads_generator import write_decoder_source


def test_generated_source_uses_mads_compatible_syntax():
    path = write_decoder_source()
    content = path.read_text(encoding="utf-8")

    assert ".ORG" in content
    assert "LDA" in content
    assert "STA" in content
    assert "RTS" in content
    assert "$C000" in content
