from __future__ import annotations

import math
from typing import Iterable

GTIA_PALETTE_16 = [
    (0x00, 0x00, 0x00),
    (0x00, 0x00, 0xAA),
    (0xAA, 0x00, 0x00),
    (0xAA, 0x00, 0xAA),
    (0x00, 0xAA, 0x00),
    (0x00, 0xAA, 0xAA),
    (0xAA, 0xAA, 0x00),
    (0xAA, 0xAA, 0xAA),
    (0xFF, 0xAA, 0x00),
    (0xAA, 0x55, 0x00),
    (0x00, 0xFF, 0x00),
    (0x00, 0xFF, 0xFF),
    (0x55, 0x55, 0xFF),
    (0xFF, 0x00, 0xFF),
    (0xFF, 0xFF, 0x00),
    (0xFF, 0xFF, 0xFF),
]

REAL_PALETTE = [
    0x323132, 0x3f3e3f, 0x4d4c4d, 0x5b5b5b,
    0x6a696a, 0x797879, 0x888788, 0x979797,
    0xa1a0a1, 0xafafaf, 0xbebebe, 0xcecdce,
    0xdbdbdb, 0xebeaeb, 0xfafafa, 0xffffff,
    0x612e00, 0x6c3b00, 0x7a4a00, 0x885800,
    0x94670c, 0xa5761b, 0xb2842a, 0xc1943a,
    0xca9d43, 0xdaad53, 0xe8bb62, 0xf8cb72,
    0xffd87f, 0xffe88f, 0xfff79f, 0xffffae,
    0x6c2400, 0x773000, 0x844003, 0x924e11,
    0x9e5d22, 0xaf6c31, 0xbc7b41, 0xcc8a50,
    0xd5935b, 0xe4a369, 0xf2b179, 0xffc289,
    0xffcf97, 0xffdfa6, 0xffedb5, 0xfffdc4,
    0x751618, 0x812324, 0x8f3134, 0x9d4043,
    0xaa4e50, 0xb85e60, 0xc66d6f, 0xd57d7f,
    0xde8787, 0xed9596, 0xfca4a5, 0xffb4b5,
    0xffc2c4, 0xffd1d3, 0xffe0e1, 0xffeff0,
    0x620e71, 0x6e1b7c, 0x7b2a8a, 0x8a3998,
    0x9647a5, 0xa557b5, 0xb365c3, 0xc375d1,
    0xcd7eda, 0xdc8de9, 0xea97f7, 0xf9acff,
    0xffbaff, 0xffc9ff, 0xffd9ff, 0xffe8ff,
    0x560f87, 0x611d90, 0x712c9e, 0x7f3aac,
    0x8d48ba, 0x9b58c7, 0xa967d5, 0xb877e5,
    0xc280ed, 0xd090fc, 0xdf9fff, 0xeeafff,
    0xfcbdff, 0xffccff, 0xffdbff, 0xffeaff,
    0x461695, 0x5122a0, 0x6032ac, 0x6e41bb,
    0x7c4fc8, 0x8a5ed6, 0x996de3, 0xa87cf2,
    0xb185fb, 0xc095ff, 0xcfa3ff, 0xdfb3ff,
    0xeec1ff, 0xfcd0ff, 0xffdfff, 0xffefff,
    0x212994, 0x2d359f, 0x3d44ad, 0x4b53ba,
    0x5961c7, 0x686fd5, 0x777ee2, 0x878ef2,
    0x9097fa, 0x96a6ff, 0xaeb5ff, 0xbfc4ff,
    0xcdd2ff, 0xdae3ff, 0xeaf1ff, 0xfafeff,
    0x0f3584, 0x1c418d, 0x2c509b, 0x3a5eaa,
    0x486cb7, 0x587bc5, 0x678ad2, 0x7699e2,
    0x80a2eb, 0x8fb2f9, 0x9ec0ff, 0xadd0ff,
    0xbdddff, 0xcbecff, 0xdbfcff, 0xeaffff,
    0x043f70, 0x114b79, 0x215988, 0x2f6896,
    0x3e75a4, 0x4d83b2, 0x5c92c1, 0x6ca1d2,
    0x74abd9, 0x83bae7, 0x93c9f6, 0xa2d8ff,
    0xb1e6ff, 0xc0f5ff, 0xd0ffff, 0xdeffff,
    0x005918, 0x006526, 0x0f7235, 0x1d8144,
    0x2c8e50, 0x3b9d60, 0x4aac6f, 0x59bb7e,
    0x63c487, 0x72d396, 0x82e2a5, 0x92f1b5,
    0x9ffec3, 0xaeffd2, 0xbeffe2, 0xcefff1,
    0x075c00, 0x146800, 0x227500, 0x328300,
    0x3f910b, 0x4fa01b, 0x5eae2a, 0x6ebd3b,
    0x77c644, 0x87d553, 0x96e363, 0xa7f373,
    0xb3fe80, 0xc3ff8f, 0xd3ffa0, 0xe3ffb0,
    0x1a5600, 0x286200, 0x367000, 0x457e00,
    0x538c00, 0x629b07, 0x70a916, 0x80b926,
    0x89c22f, 0x99d13e, 0xa8df4d, 0xb7ef5c,
    0xc5fc6b, 0xd5ff7b, 0xe3ff8b, 0xf3ff99,
    0x334b00, 0x405700, 0x4d6500, 0x5d7300,
    0x6a8200, 0x7a9100, 0x889e0f, 0x98ae1f,
    0xa1b728, 0xbac638, 0xbfd548, 0xcee458,
    0xdcf266, 0xebff75, 0xfaff85, 0xffff95,
    0x4b3c00, 0x584900, 0x655700, 0x746500,
    0x817400, 0x908307, 0x9f9116, 0xaea126,
    0xb7aa2e, 0xc7ba3e, 0xd5c74d, 0xe5d75d,
    0xf2e56b, 0xfef47a, 0xffff8b, 0xffff9a,
    0x602e00, 0x6d3a00, 0x7a4900, 0x895800,
    0x95670a, 0xa4761b, 0xb2832a, 0xc2943a,
    0xcb9d44, 0xdaac53, 0xe8ba62, 0xf8cb73,
    0xffd77f, 0xffe791, 0xfff69f, 0xffffaf,
]


class RGBColor(tuple):
    def __new__(cls, r: int, g: int, b: int):
        return super().__new__(cls, (r, g, b))

    @property
    def r(self) -> int:
        return self[0]

    @property
    def g(self) -> int:
        return self[1]

    @property
    def b(self) -> int:
        return self[2]


def _rgb2lab(color: RGBColor) -> tuple[float, float, float]:
    var_r = color.r / 255.0
    var_g = color.g / 255.0
    var_b = color.b / 255.0

    if var_r > 0.04045:
        var_r = ((var_r + 0.055) / 1.055) ** 2.4
    else:
        var_r = var_r / 12.92
    if var_g > 0.04045:
        var_g = ((var_g + 0.055) / 1.055) ** 2.4
    else:
        var_g = var_g / 12.92
    if var_b > 0.04045:
        var_b = ((var_b + 0.055) / 1.055) ** 2.4
    else:
        var_b = var_b / 12.92

    var_r *= 100.0
    var_g *= 100.0
    var_b *= 100.0

    x = var_r * 0.4124 + var_g * 0.3576 + var_b * 0.1805
    y = var_r * 0.2126 + var_g * 0.7152 + var_b * 0.0722
    z = var_r * 0.0193 + var_g * 0.1192 + var_b * 0.9505

    var_x = x / 95.047
    var_y = y / 100.0
    var_z = z / 108.883

    if var_x > 0.008856:
        var_x = var_x ** (1.0 / 3.0)
    else:
        var_x = (7.787 * var_x) + (16.0 / 116.0)
    if var_y > 0.008856:
        var_y = var_y ** (1.0 / 3.0)
    else:
        var_y = (7.787 * var_y) + (16.0 / 116.0)
    if var_z > 0.008856:
        var_z = var_z ** (1.0 / 3.0)
    else:
        var_z = (7.787 * var_z) + (16.0 / 116.0)

    lab_l = 116.0 * var_y - 16.0
    lab_a = 500.0 * (var_x - var_y)
    lab_b = 200.0 * (var_y - var_z)
    return lab_l, lab_a, lab_b


def rgb_to_atari_index(r: int, g: int, b: int) -> int:
    if not 0 <= r <= 255 or not 0 <= g <= 255 or not 0 <= b <= 255:
        raise ValueError("RGB values must be between 0 and 255")

    find = RGBColor(r, g, b)
    find_lab = _rgb2lab(find)
    k1 = 0.045
    k2 = 0.015
    best_index = 0
    best_score = float("inf")

    palette_values = list(GTIA_PALETTE_16)
    for index in range(16):
        red, green, blue = palette_values[index]
        palette_color = RGBColor(red, green, blue)
        lab_l, lab_a, lab_b = _rgb2lab(palette_color)
        c1 = math.sqrt(find_lab[1] * find_lab[1] + find_lab[2] * find_lab[2])
        c2 = math.sqrt(lab_a * lab_a + lab_b * lab_b)
        sl = 1.0
        sc = 1.0 + k1 * c1
        sh = 1.0 + k2 * c1
        dl = find_lab[0] - lab_l
        dc = c1 - c2
        a2 = find_lab[1] - lab_a
        b2 = find_lab[2] - lab_b
        dh_term = a2 * a2 + b2 * b2 - dc * dc
        dh = math.sqrt(max(0.0, dh_term))
        score = (dl / sl) ** 2 + (dc / sc) ** 2 + (dh / sh) ** 2
        if score < best_score:
            best_score = score
            best_index = index

    return best_index


def atari_index_to_rgb(index: int) -> tuple[int, int, int]:
    if not 0 <= index <= 255:
        raise ValueError("Atari color index must be between 0 and 255")
    if 0 <= index < len(GTIA_PALETTE_16):
        return GTIA_PALETTE_16[index]
    value = REAL_PALETTE[index]
    return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)


def build_palette_lookup(palette_colors: Iterable[int] | None = None) -> list[tuple[int, int, int]]:
    if palette_colors is None:
        return [atari_index_to_rgb(index) for index in range(256)]
    values = list(palette_colors)
    if len(values) == 0:
        return [(0, 0, 0)] * 256
    if len(values) == 1:
        values = values * 4
    if len(values) == 2:
        values = values + [values[0], values[1]]
    if len(values) == 3:
        values = values + [values[2]]
    if len(values) > 4:
        values = values[:4]

    resolved: list[tuple[int, int, int]] = []
    for value in values:
        if isinstance(value, (tuple, list)) and len(value) == 3:
            resolved.append((int(value[0]), int(value[1]), int(value[2])))
        else:
            resolved.append(atari_index_to_rgb(int(value) & 0xFF))
    return resolved
