from pathlib import Path
from image_io import load_binary_image_2bpp
from encoder import encode_image
from png_export import decompress, _expand_pixels
import tempfile
from block_utils import split_image_into_blocks
from encoder import encode_block

p = Path(r'c:/temp/witcher3.bin')
img = load_binary_image_2bpp(p, 160, 192)
blocks = split_image_into_blocks(img, 8)
print('block count', len(blocks))
first_block = blocks[0]
print('first block first row', first_block[0][:8])
encoded = encode_block(first_block, keep_coeffs=64)
print('encoded len', len(encoded), encoded)
from decoder_model import decode_block_payload
recons = decode_block_payload(encoded)
print('reconstructed first row', recons[:8])
print('block mismatch count', sum(1 for i, v in enumerate(recons) if v != 0))

with tempfile.TemporaryDirectory() as td:
    out = Path(td) / 'x.j650'
    encode_image(img, out, keep_coeffs=64)
    screen = decompress(out.read_bytes(), antic_mode='E')
    px = _expand_pixels(screen, 'E', 160, 192)
    for y in range(192):
        if px[y] != img[y]:
            print('first mismatch row', y)
            for idx, (a, b) in enumerate(zip(px[y], img[y])):
                if a != b:
                    print('first mismatch idx', idx, 'orig', a, 'recon', b)
                    break
            break
    else:
        print('no mismatch rows')
