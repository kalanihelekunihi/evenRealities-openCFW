#!/usr/bin/env python3
"""Bounded CASE 0xaf30 stock/C task record initialization oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_task_initialize_candidate.c'
obj=H/'transport_task_initialize.oracle.o';stub=H/'transport_task_initialize.oracle_stub.c';stubobj=H/'transport_task_initialize.oracle_stub.o';elf=H/'transport_task_initialize.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_scheduler_initialize(void){}\nvoid case_boot_task_link_reset(uint32_t x){(void)x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xaf30)
for i in range(192):
 priority=rng.randrange(1,16);mode=rng.randrange(2);task=0 if i%7==0 else 0x20002000;before=rng.randbytes(44);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,before);u.reg_write(UC_ARM_REG_R0,0x12345679);u.reg_write(UC_ARM_REG_R1,priority);u.reg_write(UC_ARM_REG_R2,mode);u.reg_write(UC_ARM_REG_R3,0x20003000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.mem_write(0x20007fc0,struct.pack('<II',0x08008559,task))
  targets=({0x0800ac84:'scheduler',0x0800bfaa:'list'} if native else {sym['case_boot_scheduler_initialize']&~1:'scheduler',sym['case_boot_task_link_reset']&~1:'list'})
  calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0)) if kind=='list' else (kind,));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800af30 if native else sym['case_boot_transport_task_initialize'])|1,0x20008000,count=1000)
  pair.append((calls,bytes(u.mem_read(0x20002000,44))))
 assert pair[0]==pair[1],(i,priority,mode,task,pair)
print('PASS_CASE_TRANSPORT_TASK_INITIALIZE',192)
