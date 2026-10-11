#!/usr/bin/env python3
"""Compare two native CASE RAM-region descriptors with independent C bodies."""
from pathlib import Path
import random,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011/application_boot_heap_regions_candidate.c'
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'regions.o';e=d/'regions.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f)
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0xbf54)
 for native,name in ((0xbf54,'case_boot_heap_region_a'),(0xbf6c,'case_boot_heap_region_b')):
  for trial in range(64):
   a,b,c=(0x20001000+4*rng.randrange(0,128) for _ in range(3))
   if len({a,b,c})<3:continue
   outcomes=[]
   for is_native in (True,False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
    u.mem_map(0x100000,0x10000)
    for addr,data in segs:u.mem_write(addr,data)
    u.mem_map(0x20000000,0x10000)
    for reg,val in ((UC_ARM_REG_R0,a),(UC_ARM_REG_R1,b),(UC_ARM_REG_R2,c),(UC_ARM_REG_SP,0x20007fc0),(UC_ARM_REG_LR,0x300001)):u.reg_write(reg,val)
    u.mem_map(0x300000,0x1000)
    u.emu_start((0x08000000+native if is_native else syms[name])|1,0x300000,count=100)
    outcomes.append((u.reg_read(UC_ARM_REG_R0),tuple(int.from_bytes(u.mem_read(x,4),'little') for x in (a,b,c))))
   assert outcomes[0]==outcomes[1],(name,trial,outcomes)
 print('PASS_CASE_HEAP_REGIONS',128)
