import importlib
import sys
from pathlib import Path


def test_rgb2a8_palette_module_is_importable_from_src_layout() -> None:
    src_root = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src_root))
    try:
        module = importlib.import_module("rgb2a8.atari_palette")
    finally:
        sys.path.remove(str(src_root))

    assert hasattr(module, "rgb_to_atari_index")
    assert hasattr(module, "atari_index_to_rgb")
