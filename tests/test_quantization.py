from quantization import quantize_block


def test_quantize_block_clamps_values_to_int8_range():
    block = [[10000 for _ in range(8)] for _ in range(8)]

    quantized = quantize_block(block)

    assert quantized[0][0] == 127
    assert all(-128 <= value <= 127 for row in quantized for value in row)
