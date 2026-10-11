#!/usr/bin/env python3
"""Compare the 0x08002fc8 initialization prefix through sensor prepare."""
from pathlib import Path
import subprocess,itertools
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
checked=0
for first_pin,second_pin,mode in itertools.product((0,1),(0,1),(0,3)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x20000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x200000bf,b'\x01');u.mem_write(0x2000087c,bytes([mode])+b'\xa5'*0x40)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   pin=(0x08004e94 if original else stubs['case_init_pin_read'])
   finish=(0x08003a30 if original else stubs['case_init_sensor_prepare'])
   if address==pin:
    base=uc.reg_read(UC_ARM_REG_R0);mask=uc.reg_read(UC_ARM_REG_R1)
    calls.append(('pin',base,mask))
    uc.reg_write(UC_ARM_REG_R0,first_pin if base==0x50000400 else second_pin)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif address==finish:
    calls.append(('prepare',));uc.emu_stop()
   elif address in ((set(stubs.values()) if not original else set())):
    raise AssertionError(('unexpected source lower',hex(address)))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08002fc8 if original else sym['case_application_initialize_2fc8'])|1,0,count=10000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x40))))
 assert pair[0]==pair[1],(first_pin,second_pin,mode,pair)
 checked+=1
print('PASS_CASE_INITIALIZATION_PREFIX',checked)
