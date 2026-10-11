"""Bounded original-byte versus source-algorithm ring-read transitions."""
from pathlib import Path
import struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,
                               UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R9,
                               UC_ARM_REG_SP)
from unicorn.unicorn_const import UC_HOOK_CODE
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DESC,BUFFER,DEST,RETURN=0x20001000,0x20003000,0x20004000,0x600000

def stock(read,write,length):
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,BLOB)
    uc.mem_map(0x20000000,0x100000)
    uc.mem_write(DESC,struct.pack('<5I',BUFFER,16,read,write,0))
    uc.mem_write(BUFFER,b'ABCDEFGHIJKLMNOP')
    uc.mem_write(DEST,b'................')
    uc.reg_write(UC_ARM_REG_SP,0x200ff000)
    uc.reg_write(UC_ARM_REG_LR,RETURN|1)
    uc.reg_write(UC_ARM_REG_R0,DESC)
    uc.reg_write(UC_ARM_REG_R1,DEST)
    uc.reg_write(UC_ARM_REG_R2,length)
    last=[0]
    def hook(m,a,s,u):
        last[0]=a
        if a==RETURN:m.emu_stop()
        elif a==0x46da1a: # ARMv8-M LDA SB,[R0]; Unicorn lacks LDA.
            value=struct.unpack('<I',m.mem_read(m.reg_read(UC_ARM_REG_R0),4))[0]
            m.reg_write(UC_ARM_REG_R9,value)
            m.reg_write(UC_ARM_REG_PC,a+5)
        elif a==0x46da6c: # ARMv8-M STL SB,[R0]; single-threaded value only.
            m.mem_write(m.reg_read(UC_ARM_REG_R0),
                        struct.pack('<I',m.reg_read(UC_ARM_REG_R9)))
            m.reg_write(UC_ARM_REG_PC,a+5)
    uc.hook_add(UC_HOOK_CODE,hook)
    try:uc.emu_start(0x46d9ad,RETURN,count=20000)
    except Exception as exc:raise RuntimeError(f'{exc} at {last[0]:#x}') from exc
    return (uc.reg_read(UC_ARM_REG_R0),
            struct.unpack('<I',uc.mem_read(DESC+8,4))[0],
            bytes(uc.mem_read(DEST,16)))

def source(read,write,length):
    out=bytearray(b'................')
    available=write+(16-read) if write<read else write-read
    count=min(length,available)
    if count==0:return (0,read,bytes(out))
    first=min(count,16-read)
    out[:first]=b'ABCDEFGHIJKLMNOP'[read:read+first]
    rest=count-first
    if rest:out[first:first+rest]=b'ABCDEFGHIJKLMNOP'[:rest]
    nxt=(rest if rest else read+first)
    if nxt>=16:nxt=0
    return (count,nxt,bytes(out))

cases=[(0,0,5),(0,5,3),(12,3,8),(15,2,8),(2,15,20),
       (7,7,1),(1,0,3)]
for case in cases:
    a,b=stock(*case),source(*case)
    assert a==b,(case,a,b)
print(f'PASS {len(cases)}/{len(cases)} stock/source-model ring reads')
