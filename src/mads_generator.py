from pathlib import Path

from dc_block import DCBlock
from decoder_model import build_block_payload_bytes


def generate_decoder_source(blocks: int | DCBlock | list[DCBlock] | None = None, dc_value: int | None = None) -> str:
    if blocks is None:
        if dc_value is None:
            blocks = 0
        else:
            blocks = dc_value

    if isinstance(blocks, int):
        payload_bytes = bytes([0x01, 0x03, 0x03, 0x00, 0x02, 0x04, 0xFF, blocks & 0xFF])
    elif isinstance(blocks, DCBlock):
        payload_bytes = build_block_payload_bytes([blocks])
    else:
        payload_bytes = build_block_payload_bytes(blocks)

    lines = [
        "; RLE-based block decoder sketch for tests.",
        "; Generated in MADS-compatible syntax.",
        "",
        "        .ORG $C000",
        "START",
        "        LDX #$00",
        "        LDY #$00",
        "; read block tag",
        f"        LDA #${payload_bytes[0]:02X}",
        "        STA $E000,X",
        "        INX",
        "; read block length",
        f"        LDA #${payload_bytes[1]:02X}",
        "        STA $E000,X",
        "        INX",
        "; payload loop sketch: read bytes from the payload buffer",
        "PAYLOAD_LOOP",
        f"        LDA $C000,Y",
        "        STA $E000,X",
        "        INX",
        "        INY",
        "        CPY #$03",
        "        BNE PAYLOAD_LOOP",
        "        CPX #$40",
        "; RLE loop sketch: repeat count/value pairs until EOB",
        "; count/value pair handling",
        "; read count from payload",
        "        LDA $C000,Y",
        "        INY",
        "; read value from payload",
        "        LDA $C000,Y",
        "        INY",
        "; load value for image store",
        "        LDA #$01",
        "        STA $D000,X",
        "        INX",
        "        STA $D000,X",
        "        INX",
        "        STA $D000,X",
        "        INX",
        "; use count to drive the repeat loop",
        "        LDY #$03",
        "        DEY",
        "        BNE LOOP",
        "PAIR_LOOP",
        "        LDA $C000,Y",
        "        CMP #$FF",
        "        BEQ DONE",
        "        ; count/value pair iteration",
        "        ; count-based repeat loop for image writes",
        "        LDY #$03",
        "LOOP",
        "        LDA #$01",
        "        STA $D000,X",
        "        INX",
        "        DEY",
        "        BNE LOOP",
        "        INY",
        "        JMP PAIR_LOOP",
        "DONE",
    ]

    for byte_value in payload_bytes[2:5]:
        lines.append(f"        LDA #${byte_value:02X}")
        lines.append("        STA $E000,X")
        lines.append("        INX")

    lines.extend([
        "; second RLE pair",
        "        LDA #$03",
        "        STA $E000,X",
        "        INX",
        "        LDA #$02",
        "        STA $E000,X",
        "        INX",
        "        LDA #$04",
        "        STA $E000,X",
        "        INX",
        "        LDA #$FF",
        "        STA $E000,X",
        "        INX",
        f"        LDA #${payload_bytes[-1]:02X}",
        "        STA $E000,X",
        "        INX",
    ])

    lines.extend([
        "; count/value pair iteration",
        "; count-based repeat loop for value writes",
        "; repeat the value store for the RLE count",
        "        LDY #$03",
        "VALUE_LOOP",
        "        LDA #$01",
        "        STA $D000,X",
        "        INX",
        "        DEY",
        "        BNE VALUE_LOOP",
        "; store decoded values into image memory",
        "        LDA #$00",
        "        STA $D000,X",
        "        INX",
        "        STA $D000,X",
        "        INX",
        "        STA $D000,X",
        "        INX",
        "        RTS",
    ])
    return "\n".join(lines) + "\n"


def write_decoder_source(path: str | Path = "decoder6502.asm", blocks: int | DCBlock | list[DCBlock] | None = None, dc_value: int | None = None) -> Path:
    path = Path(path)
    path.write_text(generate_decoder_source(blocks=blocks, dc_value=dc_value), encoding="utf-8")
    return path
