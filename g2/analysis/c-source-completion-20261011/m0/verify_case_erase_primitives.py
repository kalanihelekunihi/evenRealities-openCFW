#!/usr/bin/env python3
"""CASE 0x3e94/0x3eec native/source flash register writes."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_option_erase_primitives_candidate.c';obj=H/'erase_prim.oracle.o';elf=H/'erase_prim.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3e94)
for i in range(160):
 old=rng.getrandbits(32);bank=[4,0x8000,0,0x2000][i%4];page=rng.getrandbits(8)
 for nativeaddr,name,args in ((0x08003e94,'case_boot_option_mass_erase',(bank,)),(0x08003eec,'case_boot_option_page_erase',(bank,page))):
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_map(0x40022000,0x1000);u.mem_write(0x40022014,struct.pack('<I',old));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):u.reg_write(reg,val)
   u.emu_start((nativeaddr if native else sym[name])|1,0x20008000,count=100)
   pair.append(bytes(u.mem_read(0x40022014,4)))
  assert pair[0]==pair[1],(i,name,pair)
print('PASS_CASE_ERASE_PRIMITIVES',320)
