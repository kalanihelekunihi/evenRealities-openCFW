#!/usr/bin/env python3
"""Compare successful PMIC self-check through boost-set boundary."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/app_initialization_candidate.c'
obj=HERE/'app_initialization_candidate.o';elf=HERE/'app_initialization_candidate.elf';ld=HERE/'app_initialization_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
nm=subprocess.run(['/opt/homebrew/bin/arm-none-eabi-nm','-u',str(obj)],check=True,capture_output=True,text=True).stdout
names=sorted(line.split()[-1] for line in nm.splitlines() if line.strip())
stubs={name:0x0010f000+i*0x100 for i,name in enumerate(names)}
ld.write_text(''.join(f'{name} = 0x{address|1:08x};\n' for name,address in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
stock={'pin':0x08004e94,'prepare':0x08003a30,'read':0x080035b8,'wait':0x08004958,
       'pmic_prepare':0x08009df4,'pmic_read':0x080035d4,'hex':0x080067c8,'boost':0x08002c30}
source={k:stubs['case_init_'+{'pin':'pin_read','prepare':'sensor_prepare','read':'selfcheck_read','wait':'wait',
       'pmic_prepare':'pmic_prepare','pmic_read':'pmic_read','hex':'hex_log','boost':'boost_set'}[k]] for k in stock}
pair=[]
for original in (True,False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
 u.mem_map(0x00100000,0x20000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000)
 u.mem_write(0x200000bf,b'\x01');u.mem_write(0x2000087c,b'\x00'+b'\xa5'*0x40)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
 calls=[];address_map=stock if original else source
 def hook(uc,address,size,user):
  if address==address_map['pin']:
   calls.append(('pin',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   uc.reg_write(UC_ARM_REG_R0,0)
  elif address==address_map['prepare']:calls.append(('prepare',))
  elif address==address_map['read']:
   uc.mem_write(uc.reg_read(UC_ARM_REG_R1),b'\xa0');calls.append(('read',))
  elif address==address_map['wait']:calls.append(('wait',uc.reg_read(UC_ARM_REG_R0)))
  elif address==address_map['pmic_prepare']:calls.append(('pmic_prepare',))
  elif address==address_map['pmic_read']:
   reg=uc.reg_read(UC_ARM_REG_R0);uc.mem_write(uc.reg_read(UC_ARM_REG_R1),bytes([reg&255]));calls.append(('pmic_read',reg,uc.reg_read(UC_ARM_REG_R2)))
  elif address==address_map['hex']:calls.append(('hex',uc.reg_read(UC_ARM_REG_R1)))
  elif address==address_map['boost']:
   calls.append(('boost',uc.reg_read(UC_ARM_REG_R0)));uc.emu_stop();return
  else:return
  uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x08002fc8 if original else sym['case_application_initialize_2fc8'])|1,0,count=20000)
 pair.append((calls,bytes(u.mem_read(0x2000087c,0x40))))
assert pair[0]==pair[1],pair
print('PASS_CASE_INITIALIZATION_PMIC_SUCCESS',1)
