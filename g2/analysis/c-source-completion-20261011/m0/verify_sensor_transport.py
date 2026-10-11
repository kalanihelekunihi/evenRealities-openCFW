#!/usr/bin/env python3
"""Stock/source sensor helper call trace and return comparison at GPIO cuts."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/sensor_transport_candidate.c'
obj=HERE/'sensor_transport_candidate.o';elf=HERE/'sensor_transport_candidate.elf';ld=HERE/'sensor_transport_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
entries={'case_binary_sensor_interbyte_pulse':0x0800a3d2,'case_binary_sensor_final_pulse':0x0800a414,'case_binary_sensor_byte_input':0x0800a436,'case_binary_sensor_byte_output':0x0800a46c,'case_binary_sensor_stop':0x0800a4dc,'case_binary_sensor_ack':0x0800a4fa}
lowers=['case_binary_sensor_line_a','case_binary_sensor_line_b','case_binary_sensor_delay','case_binary_sensor_sample']
stock=[0x0800a550,0x0800a574,0x0800a408,0x0800a528]
stubs={n:0x0010f000+0x100*i for i,n in enumerate(lowers)}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stdout=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
count=0
for name,argument,sample in itertools.product(entries,[0,1,0x80,0xc8,0xff],[0,1,0x55,0xaa]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_R0,argument);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];idx=[0]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stubs.values())).index(address&~1)
   except ValueError:return
   arg=uc.reg_read(UC_ARM_REG_R0) if i in (0,1) else None
   calls.append((i,arg))
   if i==3:val=(sample>>idx[0])&1;idx[0]+=1
   elif i==2:val=10
   else:val=0x87654321
   uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((entries[name] if original else sym[name])|1,0x20001000,count=5000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,u.reg_read(UC_ARM_REG_R0) if name in ('case_binary_sensor_byte_input','case_binary_sensor_ack') else None))
 assert pair[0]==pair[1],(name,argument,sample,pair)
 count+=1
print('PASS_SENSOR_TRANSPORT',count)
