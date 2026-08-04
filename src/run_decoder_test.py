from py65.devices.mpu6502 import MPU
from asm_tools import assemble_file

memory = [0x00] * 0x10000
program = assemble_file('decoder6502.asm', origin=0xC000)
assert len(program) <= 2048
memory[0xC000:0xC000 + len(program)] = program
memory[0xD000] = 0x02
memory[0xD001] = 0xFF

mpu = MPU(memory=memory)
mpu.reset()
mpu.pc = 0xC000
for _ in range(50):
    mpu.step()
    if mpu.pc == 0xC000:
        break

assert memory[0xE000] != 0x00 or memory[0xE001] != 0x00 or memory[0xE002] != 0x00 or memory[0xE003] != 0x00
print('decoder test passed')
