#!/usr/bin/env python3
"""Native/source RAM, SCB and return comparison for scheduler primitives."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_scheduler_primitives_candidate.c';obj=H/'application_policy_scheduler_primitives.oracle.o';elf=H/'application_policy_scheduler_primitives.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xbffc)
for name,addr in [('scheduler_lock',0x0800bffc),('scheduler_unlock',0x0800c014),('task_reschedule',0x0800c0a0),('task_sleep_enter',0x0800c380)]:
 for i in range(64):
  depth=(i%7)+1;pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x2000019c,struct.pack('<I',depth));u.mem_write(0x20000158,struct.pack('<I',depth))
   u.mem_map(0xe000e000,0x1000)
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,rng.randrange(2**32))
   u.emu_start((addr if native else sym['case_policy_'+name])|1,0x20001000,count=200)
   pair.append((bytes(u.mem_read(0x20000158,4)),bytes(u.mem_read(0x2000019c,4)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_R0)))
  assert pair[0][:3]==pair[1][:3],(name,i,pair)
  if name in ('scheduler_unlock','task_reschedule'):assert pair[0][3]==pair[1][3],(name,i,pair)
 print('PASS_CASE_POLICY_'+name.upper(),64)
