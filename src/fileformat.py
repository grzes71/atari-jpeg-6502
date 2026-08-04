from __future__ import annotations

from rle import decode_rle, encode_rle

HEADER_SIZE = 12
MAGIC = b"J650"


class J650FormatError(ValueError):
    """Raised when a J650 header or block payload is malformed."""


def write_header(width: int, height: int, block_size: int = 8, reserved: int = 0) -> bytes:
    if not 0 <= width <= 65535 or not 0 <= height <= 65535:
        raise ValueError("width and height must fit in uint16")
    if not 0 <= block_size <= 255:
        raise ValueError("block_size must fit in uint8")
    if not 0 <= reserved <= 255:
        raise ValueError("reserved must fit in uint8")

    return (
        MAGIC
        + width.to_bytes(2, "little")
        + height.to_bytes(2, "little")
        + bytes([block_size, reserved, 0x00, 0x00])
    )


def read_header(payload: bytes) -> dict[str, int | str]:
    if not isinstance(payload, (bytes, bytearray)):
        raise J650FormatError("header payload must be bytes")
    if len(payload) < HEADER_SIZE:
        raise J650FormatError("payload is too short")
    if payload[:4] != MAGIC:
        raise J650FormatError("invalid magic")

    width = int.from_bytes(payload[4:6], "little")
    height = int.from_bytes(payload[6:8], "little")
    block_size = payload[8]
    reserved = payload[9]

    if width == 0 or height == 0:
        raise J650FormatError("width and height must be non-zero")
    if block_size != 8:
        raise J650FormatError("unsupported block size")
    if reserved != 0:
        raise J650FormatError("unsupported reserved value")

    return {
        "magic": payload[:4].decode("ascii"),
        "width": width,
        "height": height,
        "block_size": block_size,
        "reserved": reserved,
    }


def write_block(block_bytes: bytes) -> bytes:
    return block_bytes


def build_simple_block_payload(values: list[int] | tuple[int, ...], keep: int = 10) -> bytes:
    if len(values) != 64:
        raise ValueError("simple block payload expects 64 values")

    values_list = [int(value) & 0x03 for value in values]
    if values_list == [0] * 64:
        return bytes([0x01, 0x03, 0x40, 0x00, 0xFF])

    if keep <= 8:
        selected_pairs: list[tuple[int, int]] = []
        for index, value in enumerate(values_list):
            if value != 0:
                selected_pairs.append((index, value))
                if len(selected_pairs) >= keep:
                    break
        if selected_pairs:
            payload = bytearray([0x02])
            for index, value in selected_pairs:
                payload.append(index & 0xFF)
                payload.append(value & 0x03)
            return bytes([0x01, len(payload)]) + bytes(payload)

    packed = bytearray(16)
    for index, value in enumerate(values_list):
        byte_index = index // 4
        bit_offset = (index % 4) * 2
        if byte_index >= len(packed):
            continue
        packed[byte_index] |= (value & 0x03) << bit_offset

    return bytes([0x01, len(packed)]) + bytes(packed)


def build_sparse_coefficient_payload(
    indices: list[int],
    values: list[int],
) -> bytes:
    """Encode a sparse set of (zigzag-index, quantized-coefficient) pairs.

    The payload uses tag ``0x02`` inside a standard ``0x01`` block envelope.
    Each pair occupies 2 bytes: index (0-63) and signed 8-bit value.
    """
    if len(indices) != len(values):
        raise ValueError("indices and values must have the same length")
    if not indices:
        return bytes([0x01, 0x01, 0x02])

    inner = bytearray([0x02])
    for idx, val in zip(indices, values):
        inner.append(idx & 0x3F)
        inner.append(val & 0xFF)

    return bytes([0x01, len(inner)]) + bytes(inner)
