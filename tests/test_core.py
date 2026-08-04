import math

from basis_generator import generate_basis_blocks, reconstruct_block_from_basis_coefficients
from dct import forward_dct_2d
from quantization import dequantize_block, from_q88, quantize_block, to_q88
from zigzag import coefficients_to_block_values, zigzag_indices


def test_zigzag_has_expected_first_values():
    assert zigzag_indices[0] == 0
    assert zigzag_indices[1] == 1
    assert zigzag_indices[2] == 8
    assert zigzag_indices[3] == 16


def test_quantize_block_uses_simple_table():
    block = [[16, 0, 0, 0, 0, 0, 0, 0] for _ in range(8)]
    quantized = quantize_block(block)
    assert quantized[0][0] == 1
    assert quantized[0][1] == 0


def test_dequantize_block_restores_values():
    quantized = [[1, 0, 0, 0, 0, 0, 0, 0] for _ in range(8)]
    dequantized = dequantize_block(quantized)
    assert dequantized[0][0] == 16


def test_forward_dct_returns_real_values_for_dc():
    block = [[8 for _ in range(8)] for _ in range(8)]
    coeffs = forward_dct_2d(block)
    assert coeffs[0][0] > 0


def test_basis_generator_returns_requested_count():
    bases = generate_basis_blocks(keep=10)
    assert len(bases) == 10
    assert len(bases[0]) == 8
    assert len(bases[0][0]) == 8


def test_coefficients_to_block_values_places_values_at_zigzag_positions():
    values = coefficients_to_block_values([5, -3, 2], keep=3)

    assert len(values) == 64
    assert values[0] == 5
    assert values[1] == -3
    assert values[8] == 2
    assert values[2] == 0


def test_basis_reconstruction_from_dc_coefficient_is_clamped():
    block = reconstruct_block_from_basis_coefficients([4])

    assert len(block) == 8
    assert all(len(row) == 8 for row in block)
    assert all(0 <= value <= 3 for row in block for value in row)


def test_fixed_point_helpers_round_trip_values():
    assert from_q88(to_q88(3)) == 3
    assert from_q88(to_q88(17)) == 17
