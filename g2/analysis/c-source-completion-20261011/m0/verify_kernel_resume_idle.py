#!/usr/bin/env python3
"""Compare stock/source scheduler resume when no ready task or tick is pending."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/kernel_resume_candidate.c'
obj=HERE/'kernel_resume_candidate.o';elf=HERE/'kernel_resume_candidate.elf';ld=HERE/'kernel_resume_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_kernel_invariant_failure','case_kernel_enter','case_kernel_exit','case_kernel_list_remove','case_kernel_list_insert_tail','case_kernel_tick_increment','case_kernel_yield']
stock=[0,0x0800bffc,0x0800c014,0x0800bf2c,0x0800bfe2,0x0800ca78,0x0800c0a0]
stub={n:0x0010f000+i*0x100 for i,n in enumerate(names)}
ld.write_text(''.join(f'{n} = 0x{a|1:08x};\n' for n,a in stub.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for suspended,task_count,yield_flag in itertools.product((1,2),(0,1),(0,1)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  state=0x20000128;pending=0x2000147c
  for off,val in ((0x30,suspended),(0x08,task_count),(0x1c,yield_flag),(0x18,0)):
   u.mem_write(state+off,val.to_bytes(4,'little'))
  u.mem_write(pending,(0).to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stub.values())).index(address)
   except ValueError:return
   if i in (0,3,4,5):raise AssertionError(('unexpected lower',i))
   calls.append(i);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800cc0c if original else sym['case_kernel_scheduler_resume'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(state,0x38)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(suspended,task_count,yield_flag,pair)
 checked+=1
print('PASS_KERNEL_RESUME_IDLE',checked)
