#!/usr/bin/env python3
"""Bounded stock/source TLSF printf tail-entry domain."""
from pathlib import Path
import hashlib
import struct
import sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UcError
from unicorn import arm_const as a

root=Path(__file__).resolve().parents[4]
stock=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
path=Path(sys.argv[1])
with path.open('rb') as file:
    elf=ELFFile(file)
    segments=[(segment['p_vaddr'],segment.data()) for segment in elf.iter_segments()
              if segment['p_type']=='PT_LOAD' and segment['p_filesz']]
    names={symbol.name:symbol['st_value'] for section in elf.iter_sections()
           if section.header.sh_type=='SHT_SYMTAB' for symbol in section.iter_symbols()}

def run(original,fmt,words):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x200000);cpu.mem_map(0x20000000,0x40000)
    if original:cpu.mem_write(0x410000,stock)
    else:
        for address,data in segments:cpu.mem_write(address,data)
    cpu.mem_write(0x20010000,fmt+b'\0')
    cpu.mem_write(0x20011000,b'used\0')
    cpu.mem_write(0x200270cc,struct.pack('<I',0x20001001))
    cpu.reg_write(a.UC_ARM_REG_SP,0x2003f000)
    cpu.reg_write(a.UC_ARM_REG_LR,0x20002001)
    cpu.reg_write(a.UC_ARM_REG_R0,0x20010000)
    for reg,value in zip((a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),words):
        cpu.reg_write(reg,value)
    for index,value in enumerate(words[3:]):
        cpu.mem_write(0x2003f000+index*4,struct.pack('<I',value))
    outputs=[];done=[]
    def hook(machine,pc,size,unused):
        if original and pc==0x415f52:
            # Unicorn does not implement this stock FP64-to-FP32 instruction.
            # Model only finite round-to-nearest fixtures and retain this as
            # an explicit ISA-cut limit, not an all-FPSCR equality claim.
            bits=machine.reg_read(a.UC_ARM_REG_D0)
            number=struct.unpack('<d',struct.pack('<Q',bits))[0]
            rounded=struct.unpack('<I',struct.pack('<f',number))[0]
            machine.reg_write(a.UC_ARM_REG_S0,rounded)
            machine.reg_write(a.UC_ARM_REG_PC,pc+4|1)
        elif pc==0x20001000:
            p=machine.reg_read(a.UC_ARM_REG_R0)
            chars=[]
            for offset in range(256):
                c=machine.mem_read(p+offset,1)[0]
                if c==0:break
                chars.append(c)
            outputs.append(bytes(chars))
            machine.reg_write(a.UC_ARM_REG_PC,machine.reg_read(a.UC_ARM_REG_LR))
        elif pc==0x20002000:done.append(True);machine.emu_stop()
    cpu.hook_add(UC_HOOK_CODE,hook)
    entry=0x415fae if original else names['printf']
    try:cpu.emu_start(entry|1,0x20002002,count=200000)
    except UcError as error:
        raise RuntimeError((original,fmt,hex(cpu.reg_read(a.UC_ARM_REG_PC)),error)) from error
    assert done,(original,fmt,hex(cpu.reg_read(a.UC_ARM_REG_PC)))
    return outputs,cpu.reg_read(a.UC_ARM_REG_R0),cpu.reg_read(a.UC_ARM_REG_R1)

def double_words(value):
    bits=struct.unpack('<Q',struct.pack('<d',value))[0]
    return [bits&0xffffffff,bits>>32]

cases=[
       (b'tlsf_add_pool: Memory must be aligned by %u bytes.\n',[4,0,0]),
       (b'tlsf_add_pool: Memory size must be between %u and %u bytes.\n',[256,0x40000,0]),
       (b'tlsf_create: Memory must be aligned to %u bytes.\n',[4,0,0]),
       (b'\t%p %s size: %x (%p)\n',[0x20012000,0x20011000,0x1234,0x20011ff8]),
       (b'hex=%x unsigned=%u',[0xdeadbeef,0xffffffff,0]),
]
for fmt,words in cases:
    native=run(True,fmt,words)
    selected=run(False,fmt,words)
    assert native==selected,(fmt,native,selected)
print('PASS native/source TLSF printf entry',len(cases),'cases')
