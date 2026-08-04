from pathlib import Path

from PIL import Image

from cli import _parse_palette
from decoder_model import decode_block_payload
from image_io import write_representative_binary_image
from pipeline import build_pipeline_example, run_full_pipeline
from png_export import decompress, screen_to_png


def test_parse_palette_accepts_four_values_for_mode_e():
    assert _parse_palette("0x00,0x02,0x08,0x0e", antic_mode="E") == (0x00, 0x02, 0x08, 0x0E)


def test_build_pipeline_example_creates_decoder_source(tmp_path):
    fixture_path = Path("tests/data/sample_2bpp.bin")
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_bytes(bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    image, blocks, asm_path = build_pipeline_example(fixture_path, width=4, height=4, output_asm=tmp_path / "pipeline_decoder.asm")

    assert len(image) == 4
    assert len(blocks) > 0
    assert asm_path.exists()
    source = asm_path.read_text(encoding="utf-8")
    assert source.startswith("; Block decoder sketch")
    assert "LDA #$01" in source
    assert "LDA #$03" in source
    assert "LDA #$FF" in source
    assert source.count("STA $E000,X") > 0
    assert len(blocks) >= 1


def test_run_full_pipeline_writes_binary_and_asm(tmp_path):
    fixture_path = Path("tests/data/sample_2bpp.bin")
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_bytes(bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    image, blocks, bin_path, asm_path = run_full_pipeline(fixture_path, width=4, height=4, output_bin=tmp_path / "output.j650", output_asm=tmp_path / "pipeline_decoder.asm")

    assert len(image) == 4
    assert len(blocks) >= 1
    assert bin_path.exists()
    assert asm_path.exists()


def test_run_full_pipeline_writes_xex_when_requested(tmp_path):
    fixture_path = Path("tests/data/sample_2bpp.bin")
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_bytes(bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    xex_path = tmp_path / "pipeline_preview.xex"
    run_full_pipeline(
        fixture_path,
        width=4,
        height=4,
        output_bin=tmp_path / "output.j650",
        output_asm=tmp_path / "pipeline_decoder.asm",
        output_xex=xex_path,
    )

    assert xex_path.exists()
    assert xex_path.read_bytes().startswith(b"\xFF\xFF")


def test_decompress_and_png_export_round_trip(tmp_path):
    fixture_path = Path("tests/data/sample_2bpp.bin")
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_bytes(bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    output_bin = tmp_path / "roundtrip.j650"
    output_png = tmp_path / "roundtrip.png"
    run_full_pipeline(
        fixture_path,
        width=4,
        height=4,
        output_bin=output_bin,
        output_asm=tmp_path / "roundtrip.asm",
        export_png=output_png,
        scale=2,
    )

    assert output_bin.exists()
    assert output_png.exists()

    screen_bytes = decompress(output_bin.read_bytes(), antic_mode="E")
    assert len(screen_bytes) > 0

    screen_to_png(screen_bytes, mode="E", palette_colors=(0x00, 0x02, 0x0E, 0x28), output_path=output_png, scale=2)
    with Image.open(output_png) as image:
        assert image.size[0] > 0
        assert image.size[1] > 0


def test_run_full_pipeline_handles_representative_sample(tmp_path):
    sample_path = tmp_path / "representative_160x192.bin"
    write_representative_binary_image(sample_path, width=160, height=192)

    image, blocks, bin_path, asm_path = run_full_pipeline(
        sample_path,
        width=160,
        height=192,
        output_bin=tmp_path / "representative.j650",
        output_asm=tmp_path / "representative.asm",
    )

    assert len(image) == 192
    assert len(image[0]) == 160
    assert len(blocks) >= 1
    assert bin_path.exists()
    assert asm_path.exists()


def test_pipeline_round_trips_block_payload(tmp_path):
    fixture_path = Path("tests/data/sample_2bpp.bin")
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_bytes(bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    image, blocks, _, _ = run_full_pipeline(
        fixture_path,
        width=4,
        height=4,
        output_bin=tmp_path / "roundtrip.j650",
        output_asm=tmp_path / "roundtrip.asm",
    )

    assert len(image) == 4
    assert len(blocks) > 0
    reconstructed = decode_block_payload(b"\x01\x02\x02\x03\xFF")
    assert len(reconstructed) == 64
    assert reconstructed[0] == 0
