#!/usr/bin/env python3
"""Original/source PDM IRQ clear handle and MMIO comparison."""
import hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/pdm_irq_clear_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-pdm-clear.ld');ELF=Path('/tmp/audio-pdm-clear.elf')
LD.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,tag,instance,mask,null,old):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000);u.mem_map(0x40201000,0x5000)
 h=0x20010000;u.mem_write(h,struct.pack('<III',tag,0xa5a5a5a5,instance))
 for i in range(4):u.mem_write(0x40201000+i*0x1000+0x104,struct.pack('<II',old,old))
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301)
 u.reg_write(UC_ARM_REG_R0,0 if null else h);u.reg_write(UC_ARM_REG_R1,mask)
 writes=[]
 def write(_cpu,_access,addr,size,value,_):
  if 0x40201000<=addr<0x40206000:writes.append([addr,size,value])
 u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((symbol['audio_pdm_interrupt_clear']|1) if native else 0x5925b5,0x100300,count=100)
 return dict(result=u.reg_read(UC_ARM_REG_R0),handle=u.mem_read(h,12).hex(),writes=writes,
  final=[u.mem_read(0x40201000+i*0x1000+0x104,8).hex() for i in range(4)],sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

rows=[]
for tag in (0x01f956e2,0x03f956e2,0x01f956e3,0):
 for instance in (0,1,3):
  for mask in (0,0x18,0xffffffff):
   for null in (False,True):
    c=dict(tag=tag,instance=instance,mask=mask,null=null,old=0xa5a5a5a5)
    o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,state=o))
result=dict(status='PASS',fresh_cases=len(rows),ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),
 source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),cases=rows,
 limits=['Synthetic PDM registers and handle; no physical interrupt acknowledgement or hardware-clear behavior.'])
(D/'pdm-irq-clear-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'PDM IRQ clear original/source cases')
