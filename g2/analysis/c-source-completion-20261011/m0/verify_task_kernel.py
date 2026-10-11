#!/usr/bin/env python3
"""Compare stock/source task lookup and signal at scheduler cuts."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/task_kernel_candidates.c';obj=HERE/'task_kernel_candidates.o';elf=HERE/'task_kernel_candidates.elf';ld=HERE/'task_kernel_candidates.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_kernel_enter','case_kernel_exit','case_kernel_mode','case_kernel_queue_send','case_kernel_queue_post']
stock=[0x0800bffc,0x0800c014,0x0800ca4c,0x0800c686,0x0800c7a8]
stubs={n:0x0010f000+0x100*i for i,n in enumerate(names)}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for flags,queue,event,mode in itertools.product([0,1,2,3],[0,0x20005000],[3,6],[1,2]):
 for name in ['case_task_lookup','case_task_signal']:
  pair=[]
  for original in [True,False]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
   u.mem_map(0x00100000,0x10000)
   for a,b in segments:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20004028,bytes([flags]));u.mem_write(0x20000164,queue.to_bytes(4,'little'))
   for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x20004000,event,0x55,0x66]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
   calls=[]
   def hook(uc,address,size,user):
    try:i=(stock if original else list(stubs.values())).index(address&~1)
    except ValueError:return
    if i in [3,4]:
     ptr=uc.reg_read(UC_ARM_REG_R1);calls.append((i,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(ptr,12)),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
    else:calls.append((i,))
    val=mode if i==2 else 0x7777 if i in [3,4] else 0
    uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start(((0x0800cde4 if name=='case_task_lookup' else 0x0800cd80) if original else sym[name])|1,0x20001000,count=10000)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(name,flags,queue,event,mode,pair)
print('PASS_TASK_KERNEL',64)
