#!/usr/bin/env python3
"""Controlled task-valid and sleep-enqueue native/source comparisons."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_task_queue_candidate.c';obj=H/'application_policy_task_queue.oracle.o';elf=H/'application_policy_task_queue.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xabb0)
for kind in ('valid','enqueue'):
 for i in range(96):
  task=0x20000300;data=bytearray(0x10000);sched=0x128
  struct.pack_into('<I',data,sched,task);struct.pack_into('<I',data,sched+12,[0,10,0xfffffff0][i%3]);struct.pack_into('<I',data,sched+40,0xffffffff)
  struct.pack_into('<I',data,sched+52,0x200014a4);struct.pack_into('<I',data,sched+56,0x2000147c)
  struct.pack_into('<I',data,0x300+20,[0x200014a4,0x2000147c,0][i%3]);struct.pack_into('<I',data,0x300+40,[0,0x2000147c,7][i%3])
  ticks=[0,1,3,0xffffffff,0x30][i%5];mode=i&1;pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   u.mem_map(0x00100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes(data))
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,task if kind=='valid' else ticks);u.reg_write(UC_ARM_REG_R1,mode)
   trace=[]
   cuts=({0x0800bf2c:'unlink',0x0800bfb0:'sorted',0x0800bfe2:'insert'} if native else {sym['case_policy_task_unlink']&~1:'unlink',sym['case_policy_task_list_insert_sorted']&~1:'sorted',sym['case_policy_task_list_insert']&~1:'insert'})
   def hook(uc,addr,size,_):
    name=cuts.get(addr)
    if name is None:return
    trace.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if name!='unlink' else (name,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(0x0800b330 if kind=='valid' else 0x0800abb0) if native else sym['case_policy_task_'+('valid' if kind=='valid' else 'sleep_enqueue')]
   u.emu_start(entry|1,0x20001000,count=1000)
   pair.append((u.reg_read(UC_ARM_REG_R0) if kind=='valid' else None,bytes(u.mem_read(task,0x30)),bytes(u.mem_read(0x20000128,0x40)),trace))
  assert pair[0]==pair[1],(kind,i,pair[0],pair[1])
 print('PASS_CASE_POLICY_TASK_'+kind.upper(),96)
