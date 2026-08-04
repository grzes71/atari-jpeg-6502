from rgb2a8.atari_palette import atari_index_to_rgb, rgb_to_atari_index


def test_rgb_to_atari_index_matches_expected_near_white_and_black():
    assert rgb_to_atari_index(0, 0, 0) == 0
    assert rgb_to_atari_index(255, 255, 255) == 0x0F


def test_atari_color_zero_maps_to_black():
    assert atari_index_to_rgb(0) == (0, 0, 0)
