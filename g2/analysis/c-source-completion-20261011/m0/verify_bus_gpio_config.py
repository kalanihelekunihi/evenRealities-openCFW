#!/usr/bin/env python3
"""Compare fixed-image GPIO config with C over bounded pin/mode cases."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/bus_gpio_config_candidate.c';obj=HERE/'bus_gpio_config_candidate.o';elf=HERE/'bus_gpio_config_candidate.elf';ld=HERE/'bus_gpio_config_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
ld.write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
count=0
for base,pin,mode,remap in itertools.product([0x50000000,0x50000400],[0,1,3,7],[0,1,2,3],[0,0x10000,0x120000]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_map(0x50000000,0x10000)
  cfg=[1<<pin,mode|remap,2,1,7]
  u.mem_write(0x20004000,b''.join(x.to_bytes(4,'little') for x in cfg))
  u.reg_write(UC_ARM_REG_R0,base);u.reg_write(UC_ARM_REG_R1,0x20004000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  writes=[]
  def hook(uc,access,address,size,value,user):
   if 0x40021800<=address<0x40021900 or base<=address<base+0x100:writes.append((address,size,value))
  u.hook_add(UC_HOOK_MEM_WRITE,hook)
  u.emu_start((0x08004d30 if original else sym['case_bus_gpio_config'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append(writes)
 assert pair[0]==pair[1],(base,pin,mode,remap,pair)
 count+=1
print('PASS_BUS_GPIO_CONFIG',count)
