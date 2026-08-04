from __future__ import annotations

import subprocess
from pathlib import Path

from mads_generator import write_decoder_source


def build_with_mads(output_path: str | Path = "out_decoder.asm", dc_value: int = 0) -> subprocess.CompletedProcess[str]:
    source_path = write_decoder_source(output_path, dc_value=dc_value)
    mads = r"C:\Apps\Mad-Assembler-2.1.6\bin\windows_x86_64\mads.exe"
    if not Path(mads).exists():
        raise FileNotFoundError(f"MADS assembler not found at {mads}")

    source_text = source_path.read_text(encoding="utf-8")
    source_text = source_text.replace(".ORG", "ORG")
    source_path.write_text(source_text, encoding="utf-8")

    result = subprocess.run(
        [mads, str(source_path)],
        capture_output=True,
        text=True,
        timeout=600,
    )
    return result


def _normalize_palette(palette: tuple[int, ...] | list[int] | None, antic_mode: str = "E") -> tuple[int, ...]:
    antic_mode = antic_mode.upper()
    if palette is None:
        if antic_mode == "F":
            return (0x00, 0x0E)
        return (0x00, 0x02, 0x08, 0x0E)
    if antic_mode == "F" and len(palette) != 2:
        raise ValueError("palette must contain exactly 2 color values for ANTIC mode F")
    if antic_mode != "F" and len(palette) not in {4, 5}:
        raise ValueError("palette must contain 4 values for ANTIC modes D/E, or 5 values when including background")
    return tuple(int(value) & 0xFF for value in palette)


def _build_preview_loader_bytes(asm_bytes: bytes, start_addr: int = 0x2000, palette: tuple[int, ...] | list[int] | None = None, antic_mode: str = "E") -> bytes:
    palette_values = _normalize_palette(palette, antic_mode=antic_mode)
    antic_mode = antic_mode.upper()
    if antic_mode == "D":
        line_mode = 0x4D
    elif antic_mode == "F":
        line_mode = 0x4F
    else:
        line_mode = 0x4E

    program = bytearray()
    program.extend([0x78])  # SEI
    program.extend([0xA9, 0x00])
    program.extend([0x8D, 0x00, 0xD4])  # STA $D400

    for index, color in enumerate(palette_values):
        program.extend([0xA9, color])
        program.extend([0x8D, 0xC4 + index, 0x02])

    display_list_low_patch = len(program)
    program.extend([0xA9, 0x00])
    program.extend([0x8D, 0x30, 0x02])
    display_list_high_patch = len(program)
    program.extend([0xA9, 0x00])
    program.extend([0x8D, 0x31, 0x02])

    jsr_patch = len(program)
    program.extend([0x20, 0x00, 0x00])
    program.extend([0xA9, 0x22])
    program.extend([0x8D, 0x39, 0x02])
    program.extend([0x58])  # CLI

    loop_patch = len(program)
    program.extend([0x4C, 0x00, 0x00])

    decompress_offset = len(program)
    program.extend([0x60])  # RTS, decompressor stub

    display_list_offset = len(program)
    display_list = bytearray([0x70, 0x70, 0x70, line_mode, 0x41, 0x00, 0x00])
    program.extend(display_list)
    program.extend(asm_bytes[:32])

    display_list_addr = start_addr + display_list_offset
    program[display_list_low_patch] = display_list_addr & 0xFF
    program[display_list_high_patch] = (display_list_addr >> 8) & 0xFF

    decompress_addr = start_addr + decompress_offset
    program[jsr_patch + 1] = decompress_addr & 0xFF
    program[jsr_patch + 2] = (decompress_addr >> 8) & 0xFF

    loop_addr = start_addr + loop_patch
    program[loop_patch + 1] = loop_addr & 0xFF
    program[loop_patch + 2] = (loop_addr >> 8) & 0xFF

    return bytes(program)


def export_xex(asm_path: str | Path, output_xex: str | Path, start_addr: int = 0x2000, palette: tuple[int, ...] | list[int] | None = None, antic_mode: str = "E") -> Path:
    asm_path = Path(asm_path)
    output_xex = Path(output_xex)

    if not asm_path.exists():
        raise FileNotFoundError(f"assembly source not found: {asm_path}")

    payload = asm_path.read_bytes()
    body = _build_preview_loader_bytes(payload, start_addr=start_addr, palette=palette, antic_mode=antic_mode)

    xex = bytearray()
    xex.extend(b"\xFF\xFF")
    xex.extend((start_addr & 0xFF).to_bytes(1, "little"))
    xex.extend((start_addr >> 8).to_bytes(1, "little"))
    xex.extend(((start_addr + len(body) - 1) & 0xFF).to_bytes(1, "little"))
    xex.extend(((start_addr + len(body) - 1) >> 8).to_bytes(1, "little"))
    xex.extend(body)
    xex.extend((0xE0).to_bytes(1, "little"))
    xex.extend((0x02).to_bytes(1, "little"))
    xex.extend((0xE1).to_bytes(1, "little"))
    xex.extend((0x02).to_bytes(1, "little"))
    xex.extend((start_addr & 0xFF).to_bytes(1, "little"))
    xex.extend((start_addr >> 8).to_bytes(1, "little"))

    output_xex.write_bytes(xex)
    return output_xex
