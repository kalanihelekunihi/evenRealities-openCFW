#!/usr/bin/env python3
"""Compare stock hard-float entry with the archive's soft-float caller ABI."""
import hashlib, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[3]
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE=ROOT/'g2/components/audio/source_candidate_20261010/temperature_request_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LINK=Path('/tmp/audio-temperature-request.ld');ELF=Path('/tmp/audio-temperature-request.elf')
LINK.write_text('stock_dispatch = 0x480313; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-Og',
 '-ffreestanding','-fno-builtin','-nostdlib','-T',str(LINK),str(SOURCE),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);code=e.get_section_by_name('.text').data()
 symbol=next(s for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='stock_temperature_request')
 source_entry=symbol['st_value']|1

def run(original,fpbits,status,bound0,bound1,initial0,initial1):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x2000);u.mem_write(0x100000,code)
 u.mem_map(0x20000000,0x80000)
 u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100801)
 out=0x20010000;u.mem_write(out,struct.pack('<II',initial0,initial1))
 u.reg_write(UC_ARM_REG_R0,out)
 u.reg_write(UC_ARM_REG_R1,fpbits)
 u.reg_write(UC_ARM_REG_S0,fpbits)
 events=[];done=[False]
 def hook(cpu,addr,_size,_):
  if addr==0x100800:done[0]=True;cpu.emu_stop()
  elif addr==0x480312:
   payload=cpu.reg_read(UC_ARM_REG_R2)
   events.append(['dispatch',cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),
                  struct.unpack('<I',cpu.mem_read(payload,4))[0]])
   cpu.mem_write(payload+4,struct.pack('<II',bound0,bound1))
   cpu.reg_write(UC_ARM_REG_R0,status)
   cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(0x480029 if original else source_entry,0x100900,count=150)
 assert done[0]
 return dict(result=u.reg_read(UC_ARM_REG_R0),out=u.mem_read(out,8).hex(),
             events=events,sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

cases=[]
for fpbits in (0,0x3f800000,0xc2200000,0x7f800000,0x7fc00000,0xffffffff):
 for status in (0,1,4,0xffffffff):
  for bound0,bound1 in ((0,0),(1,2),(0x12345678,0xfedcba98)):
   for initial0,initial1 in ((0,0),(0xaaaaaaaa,0x55555555)):
    old=run(True,fpbits,status,bound0,bound1,initial0,initial1)
    new=run(False,fpbits,status,bound0,bound1,initial0,initial1)
    assert old==new,(fpbits,status,bound0,bound1,initial0,initial1,old,new)
    cases.append(dict(fpbits=fpbits,status=status,bounds=[bound0,bound1],initial=[initial0,initial1],state=old))
result=dict(status='PASS',fresh_cases=len(cases),original_entry='0x480028',
 source_abi='soft float: R0 output pointer, R1 float bits',original_abi='hard float: R0 output pointer, S0 float bits',
 ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 link_script=LINK.read_text(),cases=cases,
 limits=['The archive adapter maps the current source callers R1 bits to the stock S0 semantic input. This is not a binary ABI drop-in for original hard-float callers.',
         'The selected dispatch body is compared at its exact three-register call ABI; its callback execution is separately bounded.'])
Path(__file__).with_name('temperature-request-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'temperature request original/source ABI-adapted cases')
