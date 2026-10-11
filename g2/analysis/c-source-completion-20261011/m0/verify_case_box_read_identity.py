#!/usr/bin/env python3
"""CASE 0x2f60/0x2f88 native/source identity byte ordering."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_box_read_serial_candidate.c';obj=H/'read_id.oracle.o';elf=H/'read_id.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x2f60)
for i in range(128):
 serial=rng.randbytes(8);identity=rng.randbytes(16)
 for addr,name,size in ((0x08002f60,'case_policy_box_read_serial',8),(0x08002f88,'case_policy_box_read_identity',16)):
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x0803f000,0x1000);u.mem_write(0x0803f800,serial);u.mem_write(0x0803f000,identity);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
   u.emu_start((addr if native else sym[name])|1,0x20008000,count=200)
   pair.append(bytes(u.mem_read(0x20003000,size)))
  assert pair[0]==pair[1],(i,name,pair)
print('PASS_CASE_BOX_READ_IDENTITY',256)
