from pathlib import Path
import sys,struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'g2/analysis/audio-platform-callbacks-closure-2026-10-08'))
from itcm_record import decode_itcm
from startup_evidence import initialized_record
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];itcm=decode_itcm(raw);startup=initialized_record(raw)
elf=Path('/tmp/opencfw-hfrc-syspll/control.elf');segments=[];loaded_elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest()
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
def verified_elf_sha256():
 current=hashlib.sha256(elf.read_bytes()).hexdigest();assert current==loaded_elf_sha256,'ELF changed after test loading';return current
def w(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0,0x1000),(0x40020000,0x2000),(0x40008000,0x1000),(0x40004000,0x1000),(0xe000e000,0x2000),(0xe001e000,0x1000),(0x47ff0000,0x1000),(0x40201000,0x1000),(0x40208000,0x2000),(0x40210000,0x1000),(0x400b2000,0x1000),(0x40010000,0x2000),(0x40014000,0x1000),(0x42002000,0x2000),(0x42006000,0x4000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw);u.mem_write(0x20000000,bytes(startup));u.mem_write(0x40,itcm)
 for a,b in segments:u.mem_write(a,b)
 w(u,0xe000ed88,0xf00000);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);return u
