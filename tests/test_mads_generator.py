from asm_tools import assemble
from mads_generator import generate_decoder_source


def test_generate_decoder_source_emits_rle_payload_sketch():
    source = generate_decoder_source(dc_value=7)
    assert source.startswith("; RLE-based block decoder sketch")
    assert "LDA #$01" in source
    assert "LDA #$03" in source
    assert "LDA #$FF" in source


def test_generate_decoder_source_emits_tag_length_and_rle_bytes():
    source = generate_decoder_source(dc_value=7)

    assert "LDA #$01" in source
    assert "LDA #$03" in source
    assert "LDA #$07" in source
    assert "LDA #$FF" in source


def test_generate_decoder_source_includes_memory_store_sketch():
    source = generate_decoder_source(dc_value=7)

    assert "STA $E000,X" in source
    assert "RTS" in source


def test_generate_decoder_source_includes_rle_loop_sketch():
    source = generate_decoder_source(dc_value=7)

    assert "RLE" in source or "loop" in source.lower()


def test_generate_decoder_source_emits_multiple_rle_pairs():
    source = generate_decoder_source(dc_value=7)

    assert source.count("LDA #$03") >= 2
    assert source.count("LDA #$02") >= 1
    assert source.count("LDA #$04") >= 1


def test_generate_decoder_source_describes_rle_pair_iteration():
    source = generate_decoder_source(dc_value=7)

    assert "count/value" in source.lower() or "pair" in source.lower()


def test_generate_decoder_source_mentions_repeated_value_store():
    source = generate_decoder_source(dc_value=7)

    assert "repeat" in source.lower() or "store" in source.lower()


def test_generate_decoder_source_mentions_count_based_repeat_loop():
    source = generate_decoder_source(dc_value=7)

    assert "count" in source.lower() and "repeat" in source.lower()


def test_generate_decoder_source_emits_multiple_value_stores():
    source = generate_decoder_source(dc_value=7)

    assert source.count("STA $D000,X") >= 2


def test_generate_decoder_source_marks_count_driven_repeat_loop():
    source = generate_decoder_source(dc_value=7)

    assert "count" in source.lower() and "repeat" in source.lower() and "store" in source.lower()


def test_generate_decoder_source_reads_payload_bytes_in_loop():
    source = generate_decoder_source(dc_value=7)

    assert "LDA $C000,Y" in source or "LDA $C000,X" in source
    assert "PAYLOAD_LOOP" in source


def test_generate_decoder_source_stops_on_eob_marker():
    source = generate_decoder_source(dc_value=7)

    assert "CMP #$FF" in source
    assert "BEQ" in source


def test_generated_source_is_assembleable_by_simple_assembler():
    source = generate_decoder_source(dc_value=7)

    program = assemble(source, origin=0xC000)

    assert len(program) > 0
    assert program[0] in {0xA9, 0xA2, 0xA0, 0x8D, 0x9D, 0xAD, 0xBD, 0xB9, 0xE8, 0xC8, 0x88, 0xE0, 0xC0, 0xC9, 0xD0, 0xF0, 0x4C, 0xEA, 0x60}


def test_generate_decoder_source_uses_indexed_image_store():
    source = generate_decoder_source(dc_value=7)

    assert "STA $D000,X" in source
    assert "INX" in source


def test_generate_decoder_source_mentions_count_value_pairs():
    source = generate_decoder_source(dc_value=7)

    assert "count/value" in source.lower() or "pair" in source.lower()


def test_generate_decoder_source_mentions_count_and_value_separately():
    source = generate_decoder_source(dc_value=7)

    assert "count" in source.lower()
    assert "value" in source.lower()


def test_generate_decoder_source_reads_count_and_value_from_payload_separately():
    source = generate_decoder_source(dc_value=7)

    assert "; read count from payload\n        LDA $C000,Y" in source
    assert "; read value from payload\n        LDA $C000,Y" in source


def test_generate_decoder_source_uses_value_for_image_store():
    source = generate_decoder_source(dc_value=7)

    assert "LDA #$01" in source and "STA $D000,X" in source


def test_generate_decoder_source_uses_count_for_repeat_loop():
    source = generate_decoder_source(dc_value=7)

    assert "LDY" in source and "DEY" in source and "BNE" in source


def test_generate_decoder_source_emits_repeated_image_writes():
    source = generate_decoder_source(dc_value=7)

    assert source.count("STA $D000,X") >= 3
