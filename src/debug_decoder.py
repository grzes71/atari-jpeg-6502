from py65.devices.mpu6502 import MPU
from asm_tools import assemble_file

memory = [0x00] * 0x10000
program = assemble_file('decoder6502.asm', origin=0xC000)
print('program bytes', len(program), program)
memory[0xC000:0xC000 + len(program)] = program
memory[0xD000] = 0x02
memory[0xD001] = 0xFF

mpu = MPU(memory=memory)
mpu.reset()
mpu.pc = 0xC000
for step in range(20):
    print('before', step, hex(mpu.pc), hex(mpu.a), hex(mpu.x))
    mpu.step()
    print('after ', step, hex(mpu.pc), hex(mpu.a), hex(mpu.x))

print('memory E000-E00F', memory[0xE000:0xE010])
