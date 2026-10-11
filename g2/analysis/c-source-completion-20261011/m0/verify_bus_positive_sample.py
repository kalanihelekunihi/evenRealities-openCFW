#!/usr/bin/env python3
"""Compare stock/source positive GPIO sample under scripted transitions."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/bus_positive_sample_candidate.c';obj=HERE/'bus_positive_sample_candidate.o';elf=HERE/'bus_positive_sample_candidate.elf';ld=HERE/'bus_positive_sample_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
stubs={'case_bus_gpio_config':0x0010f000,'case_control_write':0x0010f100}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for state,pattern in itertools.product([0,1,2],[[0,1],[1,1],[0,0,1],[1,0,1]]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x50000000,0x1000)
  u.mem_write(0x20000018,state.to_bytes(4,'little'));u.mem_write(0x2000001c,state.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];reads=[0]
  def gpio(uc,access,address,size,value,user):
   if address==0x50000410:
    bit=pattern[min(reads[0],len(pattern)-1)];reads[0]+=1;uc.mem_write(address,(bit*4).to_bytes(4,'little'))
  def hook(uc,address,size,user):
   if address in [0x08004d30,stubs['case_bus_gpio_config']]:calls.append(('cfg',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   elif address in [0x08004e9e,stubs['case_control_write']]:calls.append(('write',*(uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2])))
   elif address==0x0800a794:calls.append(('delay',uc.reg_read(UC_ARM_REG_R0)))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_MEM_READ,gpio);u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b4e0 if original else sym['case_bus_positive_sample'])|1,0x20001000,count=5000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append(([c for c in calls if c[0]!='delay'],reads[0],bytes(u.mem_read(0x20003000,4)),bytes(u.mem_read(0x20000008,8)),bytes(u.mem_read(0x20000018,8)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(state,pattern,pair)
print('PASS_BUS_POSITIVE_SAMPLE',12)
