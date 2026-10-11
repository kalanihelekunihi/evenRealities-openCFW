#!/usr/bin/env python3
"""Compare stock/source queue wake at scheduler-list lower cuts."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/kernel_task_list_candidates.c'
obj=HERE/'kernel_task_list_candidates.o';elf=HERE/'kernel_task_list_candidates.elf';ld=HERE/'kernel_task_list_candidates.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_kernel_invariant_failure','case_kernel_list_insert_tail','case_kernel_list_remove','case_kernel_list_insert_ordered','case_kernel_task_delay']
stock=[0,0x0800bfe2,0x0800bf2c,0x0800bfb0,0x0800abb0]
stub={n:0x0010f000+i*0x100 for i,n in enumerate(names)}
ld.write_text(''.join(f'{n} = 0x{a|1:08x};\n' for n,a in stub.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for suspend,priority,current_priority in itertools.product((0,1),(1,3),(1,3)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  state=0x20000128;qlist=0x20004000;task=0x20005000;current=0x20006000
  for a,val in ((state,current),(state+0x30,suspend),(state+0x10,0),(qlist+0x0c,task+0x18),(task+0x18+0x0c,task),(task+0x2c,priority),(current+0x2c,current_priority)):
   u.mem_write(a,val.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,qlist);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stub.values())).index(address)
   except ValueError:return
   if i==0:raise AssertionError('unexpected fault')
   args=(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if i==1 else (uc.reg_read(UC_ARM_REG_R0),)
   calls.append((i,args));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800cba0 if original else sym['case_queue_wake'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(state,0x34)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(suspend,priority,current_priority,pair)
 checked+=1
print('PASS_KERNEL_QUEUE_WAKE',checked)
checked=0
for depth,effective in itertools.product((1,2),(1,3)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  state=0x20000128;task=0x20005000
  for a,val in ((state,task),(task+0x50,depth),(task+0x2c,effective),(task+0x4c,1)):
   u.mem_write(a,val.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,task);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stub.values())).index(address)
   except ValueError:return
   if i==0:raise AssertionError('unexpected fault')
   args=(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if i==1 else (uc.reg_read(UC_ARM_REG_R0),)
   calls.append((i,args));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800cb38 if original else sym['case_kernel_mutex_release'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(state,0x18)),bytes(u.mem_read(task,0x54)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(depth,effective,pair)
 checked+=1
print('PASS_KERNEL_MUTEX_RELEASE',checked)
