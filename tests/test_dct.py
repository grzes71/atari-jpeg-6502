from dct import forward_dct_2d, inverse_dct_2d, reconstruct_block_from_coefficients


def test_inverse_dct_round_trip_for_simple_block():
    block = [[(x * 3 + y) % 8 for x in range(8)] for y in range(8)]

    coeffs = forward_dct_2d(block)
    reconstructed = inverse_dct_2d(coeffs)

    assert len(reconstructed) == 8
    assert all(len(row) == 8 for row in reconstructed)
    assert max(abs(reconstructed[row][col] - block[row][col]) for row in range(8) for col in range(8)) < 1e-6


def test_forward_dct_of_constant_block_keeps_only_dc_coefficient():
    block = [[5 for _ in range(8)] for _ in range(8)]

    coeffs = forward_dct_2d(block)

    assert coeffs[0][0] > 0
    assert all(abs(coeffs[row][col]) < 1e-6 for row in range(1, 8) for col in range(8))
    assert all(abs(coeffs[row][col]) < 1e-6 for row in range(8) for col in range(1, 8))


def test_reconstruct_block_from_coefficients_zero_fills_missing_terms():
    reconstructed = reconstruct_block_from_coefficients([4])

    assert len(reconstructed) == 8
    assert all(len(row) == 8 for row in reconstructed)
    assert all(0 <= value <= 3 for row in reconstructed for value in row)
