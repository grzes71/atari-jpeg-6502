from __future__ import annotations

import math

from metrics import compute_all_metrics, psnr, ssim


class TestPSNR:
    def test_identical_images_give_inf(self) -> None:
        img = [[128, 128], [128, 128]]
        assert psnr(img, img) == float("inf")

    def test_half_value_mismatch(self) -> None:
        original = [[255, 0], [0, 255]]
        distorted = [[128, 0], [0, 255]]
        result = psnr(original, distorted, max_value=255.0)
        assert result < 100.0
        assert result > 0.0

    def test_shape_mismatch_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="shape"):
            psnr([[1, 2]], [[1, 2, 3]])


class TestSSIM:
    def test_identical_images_give_one(self) -> None:
        img = [[64 if (x + y) % 2 == 0 else 128 for x in range(8)] for y in range(8)]
        result = ssim(img, img, data_range=255.0)
        assert result >= 0.99

    def test_output_in_range(self) -> None:
        original = [[128, 64, 32, 200, 100, 50, 180, 90] for _ in range(8)]
        distorted = [[130, 60, 30, 198, 98, 48, 178, 88] for _ in range(8)]
        result = ssim(original, distorted, data_range=255.0)
        assert -1.0 <= result <= 1.0


class TestComputeAllMetrics:
    def test_returns_both_keys(self) -> None:
        img = [[(x * 31 + y * 17) % 256 for x in range(8)] for y in range(8)]
        metrics = compute_all_metrics(img, img)
        assert "psnr" in metrics
        assert "ssim" in metrics
        assert metrics["psnr"] == float("inf")
        assert metrics["ssim"] >= 0.99
