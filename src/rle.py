from __future__ import annotations

EOB = 0xFF


def encode_rle(values: list[int] | tuple[int, ...]) -> bytes:
    if not values:
        return bytes([EOB])

    out = bytearray()
    run_length = 1
    prev = values[0]

    for value in values[1:]:
        if value == prev and run_length < 255:
            run_length += 1
        else:
            out.append(run_length)
            out.append(prev & 0xFF)
            prev = value
            run_length = 1

    out.append(run_length)
    out.append(prev & 0xFF)
    out.append(EOB)
    return bytes(out)


def decode_rle(payload: bytes) -> list[int]:
    if not payload:
        return []

    values: list[int] = []
    idx = 0
    while idx < len(payload):
        count = payload[idx]
        if count == EOB:
            break
        idx += 1
        if idx >= len(payload):
            raise ValueError("RLE payload is truncated")
        value = payload[idx]
        if value == EOB:
            break
        idx += 1
        values.extend([value] * count)
    return values
