#!/usr/bin/env python3
"""Compare CASE native 0x01ea preserving memset wrapper with C."""
from pathlib import Path
import random,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011'
sources=[S/'application_boot_runtime_leaf_helpers_candidate.c',S/'application_boot_task_frame_candidate.c']
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);objects=[]
 for src in sources:
  o=d/(src.stem+'.o');subprocess.run(flags+[str(src),'-o',str(o)],check=True);objects.append(o)
 elf=d/'o.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objects],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 rng=random.Random(0x1ea)
 for i in range(256):
  n=i%65;value=rng.randrange(256);pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000100,bytes([0xa5])*80)
   u.reg_write(UC_ARM_REG_R0,0x20000100);u.reg_write(UC_ARM_REG_R1,value);u.reg_write(UC_ARM_REG_R2,n)
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   u.emu_start((0x080001ea if native else sym['case_boot_memset_return_start'])|1,0x20008000,count=300)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000100,80))))
  assert pair[0]==pair[1]==(0x20000100,bytes([value])*n+bytes([0xa5])*(80-n)),(i,n,value,pair)
 print('PASS_CASE_MEMSET_RETURN_START',256)
