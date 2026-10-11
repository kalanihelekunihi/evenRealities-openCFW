"""Authenticated cmap format fixtures for native glyph-index source projection."""
from pathlib import Path
import struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
FONT,INNER,RANGES,UNICODE,GLYPHS,RETURN=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x600000

def stock(kind,codepoint):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    u.mem_write(FONT+0x18,struct.pack('<I',INNER))
    u.mem_write(INNER+8,struct.pack('<I',RANGES))
    u.mem_write(INNER+0x12,struct.pack('<H',1))
    record=bytearray(20)
    struct.pack_into('<IHHIIH',record,0,100,8,20,UNICODE,GLYPHS,3)
    record[18]=kind
    u.mem_write(RANGES,bytes(record))
    if kind==0:u.mem_write(GLYPHS,bytes([0,2,0,4,0,0,0,0]))
    elif kind==1:
        u.mem_write(UNICODE,struct.pack('<3H',0,2,5))
        u.mem_write(GLYPHS,struct.pack('<3H',0,7,9))
    elif kind==3:u.mem_write(UNICODE,struct.pack('<3H',0,2,5))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,FONT);u.reg_write(UC_ARM_REG_R1,codepoint)
    u.emu_start(0x4b2775,RETURN,count=50000)
    return u.reg_read(UC_ARM_REG_R0)

cases=[(2,102,22),(2,109,0),(0,100,20),(0,101,22),(0,102,0),
       (1,102,27),(1,101,0),(3,105,22),(3,103,0)]
for kind,codepoint,expected in cases:
    actual=stock(kind,codepoint)
    assert actual==expected,(kind,codepoint,actual,expected)
print(f'PASS {len(cases)}/{len(cases)} original-byte cmap-format fixtures')
