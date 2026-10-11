#!/usr/bin/env python3
"""CASE 0x4edc tick accumulator and 0x543c clock snapshot native/source."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_clock_snapshot_helpers_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'s.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0x543c)
 for off,name in [(0x4edc,'case_boot_clock_accumulate_tick'),(0x543c,'case_boot_clock_snapshot')]:
  for i in range(160):
   tick=rng.randrange(256);accum=rng.getrandbits(32);rcc=rng.getrandbits(32);flash=rng.getrandbits(32);pairs=[]
   for native in (True,False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000118,bytes([tick]));u.mem_write(0x20000120,struct.pack('<I',accum));u.mem_write(0x20003000,bytes(24));u.mem_map(0x40021000,0x1000);u.mem_write(0x40021008,struct.pack('<I',rcc));u.mem_map(0x40022000,0x1000);u.mem_write(0x40022000,struct.pack('<I',flash));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,0x20003010)
    u.emu_start((0x08000000+off if native else sym[name])|1,0x20008000,count=200)
    pairs.append((bytes(u.mem_read(0x20000118,12)),bytes(u.mem_read(0x20003000,24))))
   assert pairs[0]==pairs[1],(hex(off),i,pairs)
 print('PASS_CASE_CLOCK_SNAPSHOT_HELPERS',320)
