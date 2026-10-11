#!/usr/bin/env python3
"""Bounded stock/source queue ring insertion at mutex and memcpy cuts."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/kernel_queue_copy_candidate.c'
obj=HERE/'kernel_queue_copy_candidate.o';elf=HERE/'kernel_queue_copy_candidate.elf';ld=HERE/'kernel_queue_copy_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('case_kernel_mutex_release = 0x0010f001;\nSECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for width in (0,1,4,7):
 for mode in (0,1,2):
  for used in (0,1):
   pair=[]
   for original in (True,False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
    u.mem_map(0x00100000,0x10000)
    for a,b in segments:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000)
    q=0x20004000;ring=0x20005000;item=0x20006000
    u.mem_write(ring,b'\xa5'*64);u.mem_write(item,b'ABCDEFGH')
    values={0:ring,1:ring+16,2:ring+32,3:ring+24,0x38//4:used,0x40//4:width}
    for idx,value in values.items():u.mem_write(q+idx*4,value.to_bytes(4,'little'))
    for reg,val in [(UC_ARM_REG_R0,q),(UC_ARM_REG_R1,item),(UC_ARM_REG_R2,mode),(UC_ARM_REG_SP,0x20008000),(UC_ARM_REG_LR,0x20001001)]:u.reg_write(reg,val)
    calls=[]
    def hook(uc,address,size,user):
     if (original and address==0x0800cb38) or (not original and address==0x0010f000):
      calls.append(('mutex',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,3);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((0x0800ad48 if original else sym['case_queue_copy_in'])|1,0x20001000,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20001000
    pair.append((bytes(u.mem_read(q,68)),bytes(u.mem_read(ring,64)),calls,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(width,mode,used,pair)
   checked+=1
print('PASS_KERNEL_QUEUE_COPY',checked)
