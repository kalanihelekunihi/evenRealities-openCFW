#!/usr/bin/env python3
"""Original/source timer-list insertion decision comparison."""
import hashlib, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[3]
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE=ROOT/'g2/components/audio/source_candidate_20261010/timer_reload_insert_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LINK=Path('/tmp/audio-timer-reload-insert.ld');ELF=Path('/tmp/audio-timer-reload-insert.elf')
LINK.write_text('audio_public_list_insert = 0x4560b3; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LINK),str(SOURCE),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);code=e.get_section_by_name('.text').data()
 symbol=next(s for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_timer_reload_insert')
 source_entry=symbol['st_value']|1

def run(original,period,next_value,now,expiry):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x2000);u.mem_write(0x100000,code)
 u.mem_map(0x20000000,0x80000)
 timer=0x20010000;state=bytearray(40);struct.pack_into('<I',state,24,period);u.mem_write(timer,bytes(state))
 u.mem_write(0x20074aa8,struct.pack('<II',0x20011000,0x20012000))
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100801)
 for reg,val in ((UC_ARM_REG_R0,timer),(UC_ARM_REG_R1,next_value),(UC_ARM_REG_R2,now),(UC_ARM_REG_R3,expiry)):u.reg_write(reg,val)
 events=[];done=[False]
 def hook(cpu,addr,_size,_):
  if addr==0x100800:done[0]=True;cpu.emu_stop()
  elif addr==0x4560b2:
   events.append(['vListInsert',cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)])
   cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start(0x47e93d if original else source_entry,0x100900,count=300)
 assert done[0]
 return dict(result=u.reg_read(UC_ARM_REG_R0),events=events,timer=u.mem_read(timer,40).hex(),
             globals=u.mem_read(0x20074aa8,8).hex(),sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

cases=[]
for period in (0,1,7,0xffffffff):
 for next_value in (0,1,7,0xfffffff0,0xffffffff):
  for now in (0,1,8,0xfffffff0,0xffffffff):
   for expiry in (0,1,9,0xfffffff0,0xffffffff):
    old=run(True,period,next_value,now,expiry);new=run(False,period,next_value,now,expiry)
    assert old==new,(period,next_value,now,expiry,old,new)
    cases.append(dict(period=period,next=next_value,now=now,expiry=expiry,state=old))
result=dict(status='PASS',fresh_cases=len(cases),original_entry='0x47e93c',
 ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 link_script=LINK.read_text(),cases=cases,
 limits=['vListInsert 0x4560B2 is compared at its exact two-argument call boundary; its independently selected source and list effects are outside these cases.'])
Path(__file__).with_name('timer-reload-insert-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'timer reload insert original/source cases')
