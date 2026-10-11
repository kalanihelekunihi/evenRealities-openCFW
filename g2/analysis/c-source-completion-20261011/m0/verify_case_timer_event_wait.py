#!/usr/bin/env python3
"""CASE c19c stock/C event wait child-call oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_timer_event_wait_candidate.c';obj=H/'timer_event_wait.oracle.o';stub=H/'timer_event_wait.oracle_stub.c';stubobj=H/'timer_event_wait.oracle_stub.o';elf=H/'timer_event_wait.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_task_list_insert(uint32_t a,uint32_t b){(void)a;(void)b;}\nvoid case_policy_task_sleep_enqueue(uint32_t a,uint32_t b){(void)a;(void)b;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc19c)
for i in range(96):
 ticks=rng.getrandbits(32);option=i%3==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000128,(0x20003000).to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_R1,ticks);u.reg_write(UC_ARM_REG_R2,option);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800bfe2:'insert',0x0800abb0:'enqueue'} if native else {sym['case_policy_task_list_insert']&~1:'insert',sym['case_policy_task_sleep_enqueue']&~1:'enqueue'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800c19c if native else sym['case_boot_timer_event_wait'])|1,0x20008000,count=120)
  pair.append(calls)
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_TIMER_EVENT_WAIT',96)
