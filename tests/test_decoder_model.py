import pytest

from dc_block import DCBlock
from decoder_model import build_block_decoder_source, build_block_payload_bytes, decode_block_payload


def test_build_block_decoder_source_emits_64_writes():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = build_block_decoder_source(block)
    assert source.count("LDA #$") >= 10
    assert source.count("STA $E000,X") >= 10


def test_build_block_decoder_source_emits_payload_for_each_block():
    blocks = [
        DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8),
        DCBlock.from_rows(((9, 10, 11, 12, 13, 14, 15, 16),) * 8),
    ]

    source = build_block_decoder_source(blocks)

    header_sequence = "        LDA #$01\n        STA $E000,X\n        INX\n        LDA #$03"
    assert source.count(header_sequence) == 2
    assert "LDA #$09" in source
    assert "LDA #$0C" in source


def test_build_block_decoder_source_emits_real_decompressor_structure():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = build_block_decoder_source(block)

    assert "DECOMPRESS_BLOCK" in source
    assert "PAIR_DECODE" in source
    assert "IMAGE_BUFFER" in source
    assert "PAYLOAD" in source


def test_build_block_decoder_source_emits_mads_style_decode_loop():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = build_block_decoder_source(block)

    assert "DECODE_NEXT_BLOCK" in source
    assert "READ_TOKEN_PAIR" in source
    assert "WRITE_TO_IMAGE" in source
    assert "; --- decoder state ---" in source


def test_build_block_decoder_source_emits_mads_program_structure():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = build_block_decoder_source(block)

    assert "; MADS-compatible decoder skeleton" in source
    assert "; --- program entry point ---" in source
    assert "; --- helper routines ---" in source
    assert "; --- payload data ---" in source


def test_build_block_decoder_source_emits_realistic_entry_sequence():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = build_block_decoder_source(block)

    assert "JSR INIT_DECODER" in source
    assert "JSR DECOMPRESS_BLOCK" in source
    assert "INIT_DECODER" in source


def test_decode_block_payload_rebuilds_raw_block_values():
    # Payload with unrecognised inner tag falls through to zero-fill
    payload = bytes([0x01, 0x04, 0x04, 0x01, 0x01, 0x02, 0xFF])

    values = decode_block_payload(payload)

    assert values[:4] == [0x00, 0x00, 0x00, 0x00]
    assert len(values) == 64


def test_decode_block_payload_rle_decodes_runs():
    # RLE-encoded: 64 pixels of value 2
    payload = bytes([0x01, 0x04, 0x03, 64, 2, 0xFF])
    values = decode_block_payload(payload)
    assert values == [2] * 64


def test_decode_block_payload_rle_partial_fills_remaining_with_zero():
    # RLE with fewer than 64 pixels: 0x03 + 10 + 3 + 0xFF = 4 bytes
    payload = bytes([0x01, 0x04, 0x03, 10, 3, 0xFF])
    values = decode_block_payload(payload)
    assert values[:10] == [3] * 10
    assert values[10:] == [0] * 54


def test_build_block_payload_bytes_stacks_multiple_blocks():
    blocks = [
        DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8),
        DCBlock.from_rows(((9, 10, 11, 12, 13, 14, 15, 16),) * 8),
    ]

    payload = build_block_payload_bytes(blocks)

    assert payload[:7] == bytes([0x01, 0x03, 0x03, 0x00, 0x02, 0x04, 0xFF])
    assert payload[7:11] == bytes([1, 2, 3, 4])
    assert payload[11:18] == bytes([0x01, 0x03, 0x03, 0x00, 0x02, 0x04, 0xFF])


def test_decode_block_payload_rejects_truncated_payload():
    with pytest.raises(ValueError):
        decode_block_payload(bytes([0x01, 0x05, 0x02]))


def test_decode_block_payload_rebuilds_sparse_coefficients():
    payload = bytes([0x01, 0x05, 0x02, 0x08, 0x02, 0x10, 0x03, 0xFF])

    values = decode_block_payload(payload)

    assert values[:3] == [0x00, 0x00, 0x00]
    assert values[8] == 0x02
    assert values[16] == 0x03


def test_build_block_decoder_source_mentions_zero_fill_and_dequantization():
    block = DCBlock.from_rows(((1, 2, 3, 4, 5, 6, 7, 8),) * 8)
    source = build_block_decoder_source(block)

    assert "ZERO_FILL" in source
    assert "DEQUANTIZE" in source


def test_decode_block_payload_handles_eob_payload():
    values = decode_block_payload(bytes([0xFF]))

    assert values == [0] * 64


def test_decode_block_payload_handles_rle_like_sparse_payload():
    payload = bytes([0x01, 0x05, 0x02, 0x08, 0x02, 0x10, 0x03, 0xFF])

    values = decode_block_payload(payload)

    assert values[8] == 0x02
    assert values[16] == 0x03
