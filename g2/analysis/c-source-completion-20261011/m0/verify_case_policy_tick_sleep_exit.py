#!/usr/bin/env python3
"""Controlled no-wake original/source scheduler tick and sleep-exit paths."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objects=[]
for base in ('application_policy_tick_candidate','application_policy_sleep_exit_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objects.append(obj)
stub=H/'application_policy_tick_exit.oracle_stub.c';stubobj=H/'application_policy_tick_exit.oracle_stub.o';elf=H/'application_policy_tick_exit.oracle.elf'
stub.write_text('''#include <stdint.h>\nvoid case_policy_task_unlink(uint32_t x){(void)x;}\nvoid case_policy_task_list_insert(uint32_t x,uint32_t y){(void)x;(void)y;}\nvoid case_policy_task_wake_cleanup(void){}\nvoid case_policy_scheduler_lock(void){}\nuint32_t case_policy_scheduler_unlock(void){return 0;}\nuint32_t case_policy_task_reschedule(void){return 0;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objects],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xca78)
for name,addr in [('task_pended',0x0800ca78),('task_sleep_exit',0x0800cc0c)]:
 for i in range(96):
  memory=bytearray(0x10000);s=0x128;task=0x20000300
  struct.pack_into('<I',memory,s,task);struct.pack_into('<I',memory,s+12,i+1);struct.pack_into('<I',memory,s+40,0xffffffff)
  struct.pack_into('<I',memory,s+52,0x200014a4);struct.pack_into('<I',memory,s+56,0x2000147c)
  struct.pack_into('<I',memory,0x300+44,2);struct.pack_into('<I',memory,0xff4+40,i%3)
  struct.pack_into('<I',memory,s+0x30,1 if name=='task_sleep_exit' else (i&1))
  struct.pack_into('<I',memory,s+8,0);struct.pack_into('<I',memory,s+28,i&1)
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(memory))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
   cuts=({0x0800bffc:'lock',0x0800c014:'unlock'} if native else {sym['case_policy_scheduler_lock']&~1:'lock',sym['case_policy_scheduler_unlock']&~1:'unlock'})
   trace=[]
   def hook(uc,a,size,_):
    k=cuts.get(a)
    if k is None:return
    trace.append(k);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((addr if native else sym['case_policy_'+name])|1,0x20001000,count=2000)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000128,0x40)),trace))
  assert pair[0]==pair[1],(name,i,pair)
 print('PASS_CASE_POLICY_'+name.upper(),96)
