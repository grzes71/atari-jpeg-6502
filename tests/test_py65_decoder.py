from py65.devices.mpu6502 import MPU

from asm_tools import assemble
from asm_tools import assemble_file
from mads_generator import generate_decoder_source


class SimpleMemory(list):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list.__getitem__(self, item)
        if item < 0:
            raise IndexError(item)
        if item >= len(self):
            self.extend([0x00] * (item - len(self) + 1))
        return list.__getitem__(self, item)


def test_simple_decoder_program_executes():
    memory = SimpleMemory([0x00] * 0x10000)
    program = assemble_file("decoder6502.asm", origin=0xC000)
    assert len(program) <= 2048, f"decoder exceeds 2KB limit: {len(program)} bytes"
    memory[0xC000 : 0xC000 + len(program)] = program

    mpu = MPU(memory=memory)
    mpu.reset()
    mpu.pc = 0xC000
    mpu.step()

    assert mpu.pc >= 0xC000


def test_generated_decoder_sketch_executes_under_py65():
    source = generate_decoder_source(dc_value=7)
    program = assemble(source, origin=0xC000)

    memory = SimpleMemory([0x00] * 0x10000)
    memory[0xC000 : 0xC000 + len(program)] = program
    memory[0xC000 + 0x00] = 0x01
    memory[0xC000 + 0x01] = 0x03
    memory[0xC000 + 0x02] = 0x03
    memory[0xC000 + 0x03] = 0x00
    memory[0xC000 + 0x04] = 0x02
    memory[0xC000 + 0x05] = 0x04
    memory[0xC000 + 0x06] = 0xFF
    memory[0xE000] = 0x00
    memory[0xD000] = 0x00

    mpu = MPU(memory=memory)
    mpu.reset()
    mpu.pc = 0xC000

    for _ in range(3):
        mpu.step()

    assert mpu.pc != 0xC000
