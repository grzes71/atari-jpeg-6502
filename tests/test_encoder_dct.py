from __future__ import annotations

import tempfile
from pathlib import Path

from encoder import decode_dct_archive, encode_block_dct, encode_image_dct
from fileformat import build_sparse_coefficient_payload
from image_io import load_binary_image_2bpp


def _make_test_image() -> list[list[int]]:
    return [[(x + y) % 4 for x in range(16)] for y in range(16)]


class TestSparseCoefficientPayload:
    def test_empty_indices_produces_minimal_payload(self) -> None:
        payload = build_sparse_coefficient_payload([], [])
        assert len(payload) >= 3
        assert payload[0] == 0x01

    def test_single_pair_roundtrip(self) -> None:
        payload = build_sparse_coefficient_payload([0], [5])
        assert payload[0] == 0x01
        assert payload[2] == 0x02
        assert payload[3] == 0
        assert payload[4] == 5

    def test_multiple_pairs(self) -> None:
        payload = build_sparse_coefficient_payload([0, 5, 10], [3, 7, 2])
        inner = payload[2:]
        assert inner[0] == 0x02


class TestEncodeBlockDCT:
    def test_produces_nonempty_output(self) -> None:
        block = [[1] * 8 for _ in range(8)]
        result = encode_block_dct(block, keep_coeffs=4, strategy="zigzag")
        assert len(result) > 0

    def test_all_strategies_produce_output(self) -> None:
        block = [[(x + y) % 4 for x in range(8)] for y in range(8)]
        for strategy in ("zigzag", "magnitude", "hybrid"):
            result = encode_block_dct(block, keep_coeffs=4, strategy=strategy)
            assert len(result) > 0, f"strategy {strategy} produced empty output"

    def test_zero_block_produces_empty_marker(self) -> None:
        block = [[0] * 8 for _ in range(8)]
        result = encode_block_dct(block, keep_coeffs=4, strategy="zigzag")
        assert result == b"\xff"


class TestEncodeImageDCT:
    def test_writes_valid_j650(self) -> None:
        image = _make_test_image()
        with tempfile.NamedTemporaryFile(suffix=".j650", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            encode_image_dct(image, tmp_path, keep_coeffs=4, strategy="zigzag")
            data = tmp_path.read_bytes()
            assert data[:4] == b"J650"
            assert len(data) > 12
        finally:
            tmp_path.unlink(missing_ok=True)


class TestDecodeDCTArchive:
    def test_decode_matches_image_dimensions(self) -> None:
        image = _make_test_image()
        with tempfile.NamedTemporaryFile(suffix=".j650", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            encode_image_dct(image, tmp_path, keep_coeffs=16, strategy="zigzag")
            decoded = decode_dct_archive(tmp_path)
            assert len(decoded) == 16
            assert len(decoded[0]) == 16
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_roundtrip_preserves_structure(self) -> None:
        image = _make_test_image()
        with tempfile.NamedTemporaryFile(suffix=".j650", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            encode_image_dct(image, tmp_path, keep_coeffs=64, strategy="zigzag")
            decoded = decode_dct_archive(tmp_path)
            assert len(decoded) == len(image)
            assert all(len(row) == len(image[0]) for row in decoded)
            assert all(0 <= p <= 3 for row in decoded for p in row)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_all_quant_tables_decode(self) -> None:
        image = _make_test_image()
        for qt in ("aggressive", "balanced", "fine", "default"):
            with tempfile.NamedTemporaryFile(suffix=".j650", delete=False) as tmp:
                tmp_path = Path(tmp.name)

            try:
                encode_image_dct(image, tmp_path, keep_coeffs=8, strategy="zigzag", quant_table=qt)
                decoded = decode_dct_archive(tmp_path, quant_table=qt)
                assert len(decoded) == 16
            finally:
                tmp_path.unlink(missing_ok=True)
