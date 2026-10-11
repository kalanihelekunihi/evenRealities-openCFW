#!/usr/bin/env python3
"""Compare source-owned kernel list insertion/removal against fixed stock."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/kernel_list_primitives_candidate.c'
obj=HERE/'kernel_list_primitives_candidate.o';elf=HERE/'kernel_list_primitives_candidate.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
entries={'tail':('case_kernel_list_insert_tail',0x0800bfe2),'ordered':('case_kernel_list_insert_ordered',0x0800bfb0),'remove':('case_kernel_list_remove',0x0800bf2c)}
checked=0
for kind,value1,value2 in itertools.product(('tail','ordered'),(0,3,0xffffffff),(1,5)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  base=0x20004000;item1=0x20004100;item2=0x20004200;sentinel=base+8
  for off,val in ((0,0),(4,sentinel),(8,0xffffffff),(12,sentinel),(16,sentinel)):
   u.mem_write(base+off,val.to_bytes(4,'little'))
  u.mem_write(item1,value1.to_bytes(4,'little'));u.mem_write(item2,value2.to_bytes(4,'little'))
  def call(name,r0,r1=0):
   u.reg_write(UC_ARM_REG_R0,r0);u.reg_write(UC_ARM_REG_R1,r1)
   u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
   a=entries[name][1] if original else sym[entries[name][0]]
   u.emu_start(a|1,0x20001000,count=10000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  call(kind,base,item1);call(kind,base,item2);call('remove',item1)
  pair.append((bytes(u.mem_read(base,20)),bytes(u.mem_read(item1,20)),bytes(u.mem_read(item2,20))))
 assert pair[0]==pair[1],(kind,value1,value2,pair)
 checked+=1
print('PASS_KERNEL_LISTS',checked)
