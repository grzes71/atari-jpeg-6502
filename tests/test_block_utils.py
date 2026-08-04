from block_utils import split_image_into_blocks


def test_split_image_into_blocks_returns_expected_count():
    image = [[0, 1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14, 15]]
    blocks = split_image_into_blocks(image, block_size=8)
    assert len(blocks) == 1
    assert blocks[0][0][0] == 0
    assert blocks[0][1][7] == 15
