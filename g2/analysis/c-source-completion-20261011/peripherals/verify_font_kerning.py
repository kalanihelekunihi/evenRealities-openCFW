"""Bounded original-byte kerning mode fixtures for C source semantics."""
from pathlib import Path
import struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
FONT,INNER,TABLE,KEYS,VALUES,CLASSES,RETURN=(0x20001000,0x20002000,0x20003000,
                                      0x20004000,0x20005000,0x20006000,0x600000)

def original(mode,fmt,left,right):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    u.mem_write(FONT+0x18,struct.pack('<I',INNER))
    u.mem_write(INNER+0xc,struct.pack('<I',TABLE))
    u.mem_write(INNER+0x12,struct.pack('<H',mode))
    if mode&0x2000:
        data=bytearray(32);data[2]=1;data[3]=2;u.mem_write(CLASSES,bytes(data))
        u.mem_write(CLASSES+0x100,bytes(data))
        u.mem_write(KEYS,bytes([0,0xFA,0,0,0,0,0,0,0,0]))
        u.mem_write(TABLE,struct.pack('<III',KEYS,CLASSES,CLASSES+0x100)+bytes([0,3,0,0]))
    elif fmt==0:
        u.mem_write(KEYS,bytes([2,3,4,5]));u.mem_write(VALUES,bytes([0xFD,7]))
        u.mem_write(TABLE,struct.pack('<III',KEYS,VALUES,2))
    else:
        u.mem_write(KEYS,struct.pack('<4H',2,3,4,5));u.mem_write(VALUES,bytes([0xFD,7]))
        u.mem_write(TABLE,struct.pack('<III',KEYS,VALUES,(1<<30)|2))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,FONT);u.reg_write(UC_ARM_REG_R1,left);u.reg_write(UC_ARM_REG_R2,right)
    u.emu_start(0x4b28ef,RETURN,count=30000)
    value=u.reg_read(UC_ARM_REG_R0)
    return value if value<0x80000000 else value-0x100000000

cases=[(0,0,2,3,-3),(0,0,4,5,7),(0,1,2,3,-3),(0,1,3,4,0),
       (0x2000,0,2,3,-6),(0x2000,0,1,3,0)]
for mode,fmt,left,right,expected in cases:
    value=original(mode,fmt,left,right)
    assert value==expected,(mode,fmt,left,right,value,expected)
print(f'PASS {len(cases)}/{len(cases)} original-byte kerning format/class fixtures')
