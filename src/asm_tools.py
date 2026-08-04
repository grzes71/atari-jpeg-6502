from __future__ import annotations

from pathlib import Path


def _parse_value(token: str) -> int:
    token = token.strip()
    if token.startswith("#"):
        token = token[1:]
    if token.endswith(",x") or token.endswith(",X"):
        token = token[:-2]
    if token.endswith(",y") or token.endswith(",Y"):
        token = token[:-2]
    if token.startswith("$"):
        return int(token[1:], 16)
    if token.startswith("%"):
        return int(token[1:], 2)
    if token.startswith("0x"):
        return int(token[2:], 16)
    return int(token, 10)


def assemble(source: str, origin: int = 0xC000) -> list[int]:
    program: list[int] = []
    labels: dict[str, int] = {}
    addr = origin

    lines = [line.split(";", 1)[0].strip() for line in source.splitlines()]
    for line in lines:
        if not line:
            continue
        if line.lower().startswith(".org") or line.lower().startswith("org"):
            _, value = line.split(maxsplit=1)
            addr = _parse_value(value)
            continue
        if line.endswith(":"):
            labels[line[:-1]] = addr
            continue
        if line.upper() in {"START", "PAYLOAD_LOOP", "PAIR_LOOP", "LOOP", "VALUE_LOOP", "DONE"}:
            labels[line.upper()] = addr
            continue

        op = line.split()[0].lower()
        if op == "lda":
            addr += 2
            continue
        if op == "sta":
            addr += 2
            continue
        if op in {"ldx", "ldy", "inx", "iny", "dey", "cpx", "cpy", "cmp", "bne", "beq", "rts", "nop", "jmp"}:
            if op in {"ldx", "ldy", "cpx", "cpy"}:
                addr += 2
            elif op == "jmp":
                addr += 3
            else:
                addr += 1
            continue
        raise ValueError(f"unsupported instruction: {line}")

    addr = origin
    for line in lines:
        if not line:
            continue
        if line.lower().startswith(".org") or line.lower().startswith("org"):
            _, value = line.split(maxsplit=1)
            addr = _parse_value(value)
            continue
        if line.endswith(":"):
            continue
        if line.upper() in {"START", "PAYLOAD_LOOP", "PAIR_LOOP", "LOOP", "VALUE_LOOP", "DONE"}:
            continue

        parts = line.split()
        op = parts[0].lower()
        if op == "lda":
            operand = parts[1]
            if operand.startswith("#"):
                program.append(0xA9)
                program.append(_parse_value(operand))
            elif operand.endswith(",x"):
                program.append(0xBD)
                address = _parse_value(operand[:-2])
                program.append(address & 0xFF)
                program.append((address >> 8) & 0xFF)
            elif operand.endswith(",y"):
                program.append(0xB9)
                address = _parse_value(operand[:-2])
                program.append(address & 0xFF)
                program.append((address >> 8) & 0xFF)
            else:
                program.append(0xAD)
                address = _parse_value(operand)
                program.append(address & 0xFF)
                program.append((address >> 8) & 0xFF)
        elif op == "ldx":
            operand = parts[1]
            if operand.startswith("#"):
                program.append(0xA2)
                program.append(_parse_value(operand))
            else:
                raise ValueError(f"unsupported ldx mode: {line}")
        elif op == "ldy":
            operand = parts[1]
            if operand.startswith("#"):
                program.append(0xA0)
                program.append(_parse_value(operand))
            else:
                raise ValueError(f"unsupported ldy mode: {line}")
        elif op == "sta":
            operand = parts[1]
            if operand.endswith(",x"):
                address = _parse_value(operand[:-2])
                program.append(0x9D)
                program.append(address & 0xFF)
                program.append((address >> 8) & 0xFF)
            else:
                program.append(0x8D)
                address = _parse_value(operand)
                program.append(address & 0xFF)
                program.append((address >> 8) & 0xFF)
        elif op == "inx":
            program.append(0xE8)
        elif op == "iny":
            program.append(0xC8)
        elif op == "dey":
            program.append(0x88)
        elif op == "cpx":
            program.append(0xE0)
            program.append(_parse_value(parts[1]))
        elif op == "cpy":
            program.append(0xC0)
            program.append(_parse_value(parts[1]))
        elif op == "cmp":
            program.append(0xC9)
            program.append(_parse_value(parts[1]))
        elif op == "bne":
            program.append(0xD0)
            program.append(0x00)
        elif op == "beq":
            program.append(0xF0)
            program.append(0x00)
        elif op == "jmp":
            program.append(0x4C)
            program.append(0x00)
            program.append(0x00)
        elif op == "nop":
            program.append(0xEA)
        elif op == "rts":
            program.append(0x60)
        else:
            raise ValueError(f"unsupported instruction: {line}")

    return program


def assemble_file(path: str | Path, origin: int = 0xC000) -> list[int]:
    candidates: list[Path] = []
    if path is not None:
        path_obj = Path(path)
        if path_obj.is_absolute():
            candidates.append(path_obj)
        else:
            candidates.extend([
                path_obj,
                Path(__file__).resolve().parent / path_obj,
                Path(__file__).resolve().parents[1] / path_obj,
            ])

    for candidate in candidates:
        if candidate.exists():
            return assemble(candidate.read_text(encoding="utf-8"), origin=origin)

    if candidates:
        return assemble(candidates[0].read_text(encoding="utf-8"), origin=origin)

    raise FileNotFoundError(path)
