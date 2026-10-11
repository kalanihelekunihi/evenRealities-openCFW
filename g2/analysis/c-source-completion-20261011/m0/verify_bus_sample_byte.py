#!/usr/bin/env python3
"""Compare stock/source byte assembler and parity response at bit cuts."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/bus_sample_byte_candidate.c';obj=HERE/'bus_sample_byte_candidate.o';elf=HERE/'bus_sample_byte_candidate.elf';ld=HERE/'bus_sample_byte_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_bus_response_sample','case_bus_read','case_bus_start'];stock=[0x0800b53c,0x0800c412,0x0800a19a];stubs={n:0x0010f000+0x100*i for i,n in enumerate(names)}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for byte,fail in itertools.product([0,0x55,0xaa,0xff],[0,1,4,8,9]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];sample=[0]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stubs.values())).index(address&~1)
   except ValueError:return
   if i==0:
    sample[0]+=1;uc.mem_write(uc.reg_read(UC_ARM_REG_R0),((byte>>(8-sample[0]))&1).to_bytes(4,'little'));val=0 if sample[0]==fail else 1
   elif i==1:val=1 if byte.bit_count()%2 else 0;calls.append(('parity',uc.reg_read(UC_ARM_REG_R0)))
   else:calls.append(('start',uc.reg_read(UC_ARM_REG_R0)));val=0
   uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b5d6 if original else sym['case_bus_byte_sample'])|1,0x20001000,count=5000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((sample[0],bytes(u.mem_read(0x20003000,1)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(byte,fail,pair)
print('PASS_BUS_SAMPLE_BYTE',20)
