#!/usr/bin/env python3
"""Compare stock/source queue post and send fast paths at scheduler cuts."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/kernel_queue_candidates.c';obj=HERE/'kernel_queue_candidates.o';elf=HERE/'kernel_queue_candidates.elf';ld=HERE/'kernel_queue_candidates.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_kernel_invariant_failure','case_kernel_irq_save','case_kernel_irq_restore','case_queue_copy_in','case_queue_wake','case_kernel_yield','case_kernel_enter','case_kernel_exit','case_kernel_mode','case_kernel_timeout_start','case_kernel_scheduler_suspend','case_kernel_timeout_check','case_queue_is_active','case_queue_unlock','case_queue_wait','case_kernel_scheduler_resume']
stock=[0,0x080000f4,0x080000fc,0x0800ad48,0x0800cba0,0x0800c0a0,0x0800bffc,0x0800c014,0x0800ca4c,0x0800c15c,0x0800c380,0x0800c948,0x0800b080,0x0800b374,0x0800c178,0x0800cc0c]
stubs={n:0x0010f000+0x100*i for i,n in enumerate(names)}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for name,used,cap,mode,waiter in itertools.product(['case_kernel_queue_post','case_kernel_queue_send'],[0,2],[1,3],[0,2],[-1,0]):
 if mode==2 and cap!=1: continue
 if name=='case_kernel_queue_send' and used>=cap and mode!=2: continue
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);queue=0x20004000;item=0x20005000;woken=0x20006000
  for off,val in [(0x38,used),(0x3c,cap),(0x40,4),(0x24,1)]:u.mem_write(queue+off,val.to_bytes(4,'little'))
  u.mem_write(queue+0x45,bytes([waiter&255]));u.mem_write(item,b'\x55\x66\x77\x88')
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[queue,item,woken if name=='case_kernel_queue_post' else 0,mode]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stubs.values())).index(address&~1)
   except ValueError:return
   if i==0:raise AssertionError('invalid condition reached')
   args=tuple(uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]) if i in [3,4] else (uc.reg_read(UC_ARM_REG_R0),) if i==2 else ()
   calls.append((i,*args))
   val=0x77 if i==1 else 1 if i in [3,4] else 2 if i==8 else 0
   uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(((0x0800c7a8 if name=='case_kernel_queue_post' else 0x0800c686) if original else sym[name])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(queue+0x45,1)),bytes(u.mem_read(woken,4)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(name,used,cap,mode,waiter,pair)
 checked+=1
print('PASS_KERNEL_QUEUE_FAST',checked)
