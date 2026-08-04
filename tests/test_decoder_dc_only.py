from py65.devices.mpu6502 import MPU

from asm_tools import assemble_file


def test_dc_only_decoder_writes_block():
    memory = [0x00] * 0x10000
    program = assemble_file("decoder6502.asm", origin=0xC000)
    assert len(program) <= 2048, f"decoder exceeds 2KB limit: {len(program)} bytes"

    # Simple test payload: one DC coefficient = value 2, followed by EOB.
    # The decoder will be expected to fill the whole 8x8 block with the same value.
    memory[0xC000:0xC000 + len(program)] = program
    memory[0xD000] = 0x02
    memory[0xD001] = 0xFF

    mpu = MPU(memory=memory)
    mpu.reset()
    mpu.pc = 0xC000

    # Execute enough steps to finish the program.
    for _ in range(40):
        mpu.step()
        if mpu.pc == 0xC000:
            break

    # The decoder should write at least a few pixels into the framebuffer area.
    assert memory[0xE000] != 0x00 or memory[0xE001] != 0x00 or memory[0xE002] != 0x00 or memory[0xE003] != 0x00
