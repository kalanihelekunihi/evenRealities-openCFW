#!/usr/bin/env python3
"""Compare stock/source nested critical state and scheduler mode."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/kernel_small_leaves_candidate.c';obj=HERE/'kernel_small_leaves_candidate.o';elf=HERE/'kernel_small_leaves_candidate.elf';ld=HERE/'kernel_small_leaves_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('case_kernel_nesting_underflow = 0x0010f001;\nSECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
entries={'case_kernel_enter':0x0800bffc,'case_kernel_exit':0x0800c014,'case_kernel_mode':0x0800ca4c}
count=0
for name,depth,active,suspend in itertools.product(entries,[1,2,3],[0,1],[0,1]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000019c,depth.to_bytes(4,'little'))
  u.mem_write(0x2000013c,active.to_bytes(4,'little'));u.mem_write(0x20000158,suspend.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((entries[name] if original else sym[name])|1,0x20001000,count=1000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((bytes(u.mem_read(0x2000019c,4)),u.reg_read(UC_ARM_REG_R0) if name=='case_kernel_mode' else None,u.reg_read(UC_ARM_REG_CPSR)&0x80))
 assert pair[0]==pair[1],(name,depth,active,suspend,pair)
 count+=1
print('PASS_KERNEL_SMALL_LEAVES',count)
