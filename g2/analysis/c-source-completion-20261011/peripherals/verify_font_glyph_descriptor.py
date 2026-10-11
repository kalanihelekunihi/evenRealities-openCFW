"""Bounded original-byte FreeType descriptor versus source-field model."""
from pathlib import Path
import struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
from unicorn.unicorn_const import UC_HOOK_CODE
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
FONT,INNER,METRICS,DEST,RETURN=0x20002000,0x20003000,0x20004000,0x20001000,0x600000

def fixture(codepoint,previous,kerning,missing):
    inner=bytearray(32)
    struct.pack_into('<I',inner,4,METRICS)
    struct.pack_into('<I',inner,12,1 if kerning else 0)
    struct.pack_into('<H',inner,16,32)
    struct.pack_into('<H',inner,18,0xc600)
    metrics=bytearray(96)
    # glyph index two, native metrics offset is 2 * 16.
    struct.pack_into('<I',metrics,32+4,64)
    struct.pack_into('<HHHH',metrics,32+8,9,4,3,2)
    return inner,metrics

def stock(codepoint,previous,kerning,missing):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    inner,metrics=fixture(codepoint,previous,kerning,missing)
    u.mem_write(FONT+24,struct.pack('<I',INNER))
    u.mem_write(INNER,bytes(inner));u.mem_write(METRICS,bytes(metrics))
    u.mem_write(DEST,b'?'*32)
    u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,RETURN|1)
    for reg,val in [(UC_ARM_REG_R0,FONT),(UC_ARM_REG_R1,DEST),
                    (UC_ARM_REG_R2,codepoint),(UC_ARM_REG_R3,previous)]:u.reg_write(reg,val)
    last=[0];lookup=[0];kerns=[0]
    def hook(m,a,s,user):
        last[0]=a
        if a==RETURN:m.emu_stop()
        elif a==0x4b2774:
            lookup[0]+=1
            result=(0 if missing and lookup[0]==1 else (2 if lookup[0]==1 else 3))
            m.reg_write(UC_ARM_REG_R0,result)
            m.reg_write(UC_ARM_REG_PC,m.reg_read(UC_ARM_REG_LR))
        elif a==0x4b28ee:
            kerns[0]+=1
            m.reg_write(UC_ARM_REG_R0,5)
            m.reg_write(UC_ARM_REG_PC,m.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start(0x4b26a5,RETURN,count=20000)
    except Exception as exc:raise RuntimeError(f'{exc} at {last[0]:#x}') from exc
    return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DEST,32)),lookup[0],kerns[0]

def model(codepoint,previous,kerning,missing):
    out=bytearray(b'?'*32)
    if missing:return 0,bytes(out),1,0
    lookup=2 if kerning else 1
    k=5 if kerning else 0
    advance=128 if codepoint==9 else 64
    struct.pack_into('<H',out,4,(((32*k)>>4)+advance+8)>>4)
    struct.pack_into('<HHHH',out,6,18 if codepoint==9 else 9,4,3,2)
    out[14]=((0xc600>>9)&15)+16
    out[15]&=0xfe
    struct.pack_into('<I',out,24,2)
    return 1,bytes(out),lookup,1 if kerning else 0

cases=[(65,0,False,True),(65,0,False,False),(65,66,True,False),(9,66,True,False)]
for case in cases:
    a,b=stock(*case),model(*case)
    assert a==b,(case,a,b)
print(f'PASS {len(cases)}/{len(cases)} original-byte/source-model FreeType descriptor cuts')
