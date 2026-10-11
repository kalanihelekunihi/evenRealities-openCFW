#!/usr/bin/env python3
"""Compare stock/source 0x0610 transaction at serial/response boundaries."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/binary_3f_bus_candidate.c';obj=HERE/'binary_3f_bus_candidate.o';elf=HERE/'binary_3f_bus_candidate.elf';ld=HERE/'binary_3f_bus_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_bus_prepare','case_bus_finish','case_bus_send','case_bus_start','case_bus_poll','case_bus_read']
stock=[0x0800a310,0x0800a24a,0x0800a2c4,0x0800a19a,0x0800c43c,0x0800c412]
stubs={n:0x0010f000+0x100*i for i,n in enumerate(names)}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for command,count,fail in itertools.product([0x02,0x42,0x4f],[0,1,2],[0,1,2,3,4]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20004000,b'\x12\x34')
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[command,3,count,0x20004000]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];poll=[0];reads=[0]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stubs.values())).index(address&~1)
   except ValueError:return
   arg=(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if i==2 else (uc.reg_read(UC_ARM_REG_R0),) if i in [3,5] else None
   calls.append((i,arg))
   if i==4:
    val=0 if fail==poll[0]+1 else 1
    uc.mem_write(uc.reg_read(UC_ARM_REG_R0),(0x77).to_bytes(4,'little'))
    poll[0]+=1
   elif i==5:
    val=0 if fail==3+reads[0] else 0x77
    reads[0]+=1
   else:val=0xdeadbeef
   uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08000610 if original else sym['case_binary_3f_bus'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(0x20000084,4)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(command,count,fail,pair)
print('PASS_BINARY_3F_BUS',45)
