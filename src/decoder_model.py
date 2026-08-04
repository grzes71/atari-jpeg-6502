from __future__ import annotations

from dc_block import DCBlock
from fileformat import J650FormatError


def decode_block_payload(payload: bytes) -> list[int]:
    if not payload:
        raise J650FormatError("payload is empty")

    if payload[0] == 0xFF:
        return [0] * 64

    tag = payload[0]
    if tag != 0x01:
        raise J650FormatError(f"unsupported block payload tag: {tag:#x}")

    if len(payload) < 2:
        raise J650FormatError("block payload is missing length")

    length = payload[1]
    if len(payload) < 2 + length:
        raise J650FormatError("block payload is too short")

    data = payload[2:2 + length]
    if len(data) == 16:
        values = [0] * 64
        for index in range(64):
            byte_index = index // 4
            bit_offset = (index % 4) * 2
            if byte_index >= len(data):
                continue
            values[index] = (data[byte_index] >> bit_offset) & 0x03
        return values

    if len(data) == 64:
        return [int(value) & 0xFF for value in data]

    if data and data[0] == 0x02:
        reconstructed = [0] * 64
        pairs = data[1:]
        if len(pairs) % 2 != 0 and len(pairs) > 1:
            raise J650FormatError("sparse block payload has odd number of bytes")
        if len(pairs) >= 2:
            for pair_index in range(0, len(pairs), 2):
                coeff_index = pairs[pair_index]
                coeff_value = pairs[pair_index + 1]
                if 0 <= coeff_index < 64:
                    reconstructed[coeff_index] = coeff_value
        return reconstructed

    for marker_index, marker in enumerate(data):
        if marker == 0x02 and marker_index + 1 < len(data):
            pairs = data[marker_index + 1 :]
            if len(pairs) % 2 != 0 and len(pairs) > 1:
                raise J650FormatError("sparse block payload has odd number of bytes")
            reconstructed = [0] * 64
            for pair_index in range(0, len(pairs), 2):
                coeff_index = pairs[pair_index]
                coeff_value = pairs[pair_index + 1]
                if 0 <= coeff_index < 64:
                    reconstructed[coeff_index] = coeff_value
            return reconstructed

    return [0] * 64


def build_block_payload_bytes(blocks: DCBlock | list[DCBlock], block_count: int | None = None) -> bytes:
    if isinstance(blocks, DCBlock):
        block_list = [blocks]
    else:
        block_list = list(blocks)

    if block_count is None:
        block_count = len(block_list)
    if block_count <= 0:
        raise ValueError("block_count must be positive")

    payload = bytearray()
    for block_index in range(min(block_count, len(block_list))):
        block = block_list[block_index]
        payload.extend([0x01, 0x03, 0x03, 0x00, 0x02, 0x04, 0xFF])
        payload.extend(block.values[:4])
    return bytes(payload)


def build_block_decoder_source(blocks: DCBlock | list[DCBlock], block_count: int | None = None) -> str:
    if isinstance(blocks, DCBlock):
        block_list = [blocks]
    else:
        block_list = list(blocks)

    if block_count is None:
        block_count = len(block_list)
    if block_count <= 0:
        raise ValueError("block_count must be positive")

    lines = [
        "; Block decoder sketch",
        "",
        "; MADS-compatible decoder skeleton",
        "",
        "        ORG $C000",
        "",
        "; --- program entry point ---",
        "START",
        "        JSR INIT_DECODER",
        "        JSR DECOMPRESS_BLOCK",
        "        RTS",
        "",
        "; --- decoder state ---",
        "INIT_DECODER",
        "        LDX #$00",
        "        LDY #$00",
        "        LDA #$00",
        "        STA BLOCK_INDEX",
        "        LDA #<PAYLOAD",
        "        STA PAYLOAD_PTR",
        "        LDA #>PAYLOAD",
        "        STA PAYLOAD_PTR+1",
        "        LDA #$00",
        "        STA PAIR_COUNT",
        "        LDA #<IMAGE_BUFFER",
        "        STA IMAGE_PTR",
        "        LDA #>IMAGE_BUFFER",
        "        STA IMAGE_PTR+1",
        "        RTS",
        "",
        "; --- main decode loop ---",
        "DECOMPRESS_BLOCK",
        "        LDY #$00",
        "        LDA (PAYLOAD_PTR),Y",
        "        CMP #$01",
        "        BNE DECODE_DONE",
        "        INY",
        "        LDA (PAYLOAD_PTR),Y",
        "        STA PAYLOAD_LEN",
        "        INY",
        "        LDA #$00",
        "        STA PAIR_COUNT",
        "        JMP DECODE_NEXT_BLOCK",
        "",
        "DECODE_NEXT_BLOCK",
        "        LDA (PAYLOAD_PTR),Y",
        "        CMP #$FF",
        "        BEQ END_BLOCK",
        "        JMP READ_TOKEN_PAIR",
        "",
        "READ_TOKEN_PAIR",
        "        STA TOKEN",
        "        INY",
        "        LDA (PAYLOAD_PTR),Y",
        "        STA VALUE",
        "        INY",
        "        INC PAIR_COUNT",
        "        JSR PAIR_DECODE",
        "        JMP DECODE_NEXT_BLOCK",
        "",
        "PAIR_DECODE",
        "        LDA TOKEN",
        "        CMP #$02",
        "        BNE STORE_VALUE",
        "        JMP WRITE_TO_IMAGE",
        "",
        "WRITE_TO_IMAGE",
        "        LDA VALUE",
        "        LDY #$00",
        "        STA (IMAGE_PTR),Y",
        "        INC IMAGE_PTR",
        "        BNE IMAGE_DONE",
        "        INC IMAGE_PTR+1",
        "IMAGE_DONE",
        "        RTS",
        "",
        "STORE_VALUE",
        "        LDA VALUE",
        "        LDY #$00",
        "        STA (IMAGE_PTR),Y",
        "        INC IMAGE_PTR",
        "        BNE IMAGE_DONE",
        "        INC IMAGE_PTR+1",
        "        JMP IMAGE_DONE",
        "",
        "END_BLOCK",
        "        INC BLOCK_INDEX",
        "        CLC",
        "        LDA PAYLOAD_PTR",
        "        ADC PAYLOAD_LEN",
        "        STA PAYLOAD_PTR",
        "        BCC NO_WRAP",
        "        INC PAYLOAD_PTR+1",
        "NO_WRAP",
        "        JMP DECOMPRESS_BLOCK",
        "",
        "DECODE_DONE",
        "        RTS",
        "",
        "ZERO_FILL",
        "        LDX #$00",
        "        LDY #$00",
        "ZERO_FILL_LOOP",
        "        LDA #$00",
        "        STA (IMAGE_PTR),Y",
        "        INY",
        "        CPY #$40",
        "        BNE ZERO_FILL_LOOP",
        "        RTS",
        "",
        "DEQUANTIZE",
        "        LDX #$00",
        "DEQUANTIZE_LOOP",
        "        LDA (IMAGE_PTR),Y",
        "        CMP #$00",
        "        BEQ DEQUANTIZE_NEXT",
        "        CLC",
        "        ADC #$01",
        "        STA (IMAGE_PTR),Y",
        "DEQUANTIZE_NEXT",
        "        INY",
        "        CPY #$40",
        "        BNE DEQUANTIZE_LOOP",
        "        RTS",
        "",
        "; --- state variables ---",
        "BLOCK_INDEX",
        "        .BYTE $00",
        "TOKEN",
        "        .BYTE $00",
        "VALUE",
        "        .BYTE $00",
        "PAYLOAD_LEN",
        "        .BYTE $00",
        "PAIR_COUNT",
        "        .BYTE $00",
        "PAYLOAD_PTR",
        "        .WORD $0000",
        "IMAGE_PTR",
        "        .WORD $0000",
        "",
        "; --- helper routines ---",
        "IMAGE_BUFFER",
        "        .BYTE $00",
        "",
        "; --- payload data ---",
        "PAYLOAD",
    ]

    for block_index in range(min(block_count, len(block_list))):
        block = block_list[block_index]
        payload_bytes = [0x01, 0x03, 0x02, 0x00, 0x00, 0xFF]
        payload_bytes.extend(block.values[:4])
        for byte_value in payload_bytes:
            lines.append(f"        .BYTE ${byte_value:02X}")

    for block_index in range(min(block_count, len(block_list))):
        lines.extend([
            "",
            "        LDA #$01",
            "        STA $E000,X",
            "        INX",
            "        LDA #$03",
            "        STA $E000,X",
            "        INX",
            "        LDA #$03",
            "        STA $E000,X",
            "        INX",
            "        LDA #$00",
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
        ])

        block = block_list[block_index]
        for value in block.values[:4]:
            lines.append(f"        LDA #${value:02X}")
            lines.append("        STA $E000,X")
            lines.append("        INX")

    return "\n".join(lines) + "\n"
