from pathlib import Path

from build_mads import build_with_mads, export_xex


def test_build_with_mads_runs_without_crashing():
    result = build_with_mads("out_decoder.asm")
    assert isinstance(result.returncode, int)
    assert result.returncode in {0, 1}

    output_path = Path("out_decoder.asm")
    assert output_path.exists()


def test_export_xex_writes_header_and_payload(tmp_path):
    asm_path = tmp_path / "viewer.asm"
    asm_path.write_text("; demo\nSTART\nRTS\n", encoding="utf-8")

    xex_path = export_xex(asm_path, tmp_path / "viewer.xex")

    assert xex_path.exists()
    payload = xex_path.read_bytes()
    assert payload[:2] == b"\xFF\xFF"
    assert payload[2:4] == (0x2000 & 0xFF).to_bytes(1, "little") + (0x2000 >> 8).to_bytes(1, "little")


def test_export_xex_embeds_preview_loader_bytes(tmp_path):
    asm_path = tmp_path / "viewer.asm"
    asm_path.write_text("; demo\nSTART\nRTS\n", encoding="utf-8")

    xex_path = export_xex(asm_path, tmp_path / "viewer.xex")

    payload = xex_path.read_bytes()
    assert b"\x78" in payload
    assert b"\x20" in payload
    assert b"\x4C" in payload
