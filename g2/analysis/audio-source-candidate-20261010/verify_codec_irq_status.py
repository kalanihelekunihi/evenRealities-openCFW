#!/usr/bin/env python3
"""Original/source UART codec IRQ status with pointer fault boundaries."""
import hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_MEM_READ_UNMAPPED, UC_HOOK_MEM_WRITE_UNMAPPED, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/codec_irq_status_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-codec-irq-status.ld');ELF=Path('/tmp/audio-codec-irq-status.elf')
LD.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),'-o',str(ELF)],check=True)
raw_image=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,tag,instance,raw,null_handle,null_out):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw_image)+4095)&~4095);u.mem_write(0x438000,raw_image)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000);u.mem_map(0x40039000,0x5000)
 h=0x20010000;out=0x20011000
 u.mem_write(h,struct.pack('<I',tag)+bytes([0xA5])*36+struct.pack('<I',instance))
 u.mem_write(out,struct.pack('<I',0xa5a5a5a5))
 for i in range(4):u.mem_write(0x40039000+i*0x1000+0x3c,struct.pack('<II',0x11223300+i,0x55667700+i))
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301)
 u.reg_write(UC_ARM_REG_R0,0 if null_handle else h);u.reg_write(UC_ARM_REG_R1,0 if null_out else out);u.reg_write(UC_ARM_REG_R2,raw)
 writes=[];fault=[]
 def write(_cpu,_access,addr,size,value,_):
  if addr==out:writes.append([addr,size,value])
 def bad(cpu,access,addr,size,value,_):
  fault.append([access,addr,size,value]);cpu.emu_stop();return True
 u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ_UNMAPPED,bad);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,bad)
 try:u.emu_start((symbol['codec_irq_status']|1) if native else 0x58e80f,0x100300,count=100)
 except UcError:
  if not fault:raise
 return dict(result=None if fault else u.reg_read(UC_ARM_REG_R0),fault=fault,handle=u.mem_read(h,44).hex(),
  out=u.mem_read(out,4).hex(),writes=writes,sp=u.reg_read(UC_ARM_REG_SP),pc=None if fault else u.reg_read(UC_ARM_REG_PC))

rows=[]
for tag in (0x01ea9e06,0x03ea9e06,0x01ea9e07,0):
 for instance in (0,1,3):
  for raw in (0,1,0x100):
   for null_handle in (False,True):
    for null_out in (False,True):
     c=dict(tag=tag,instance=instance,raw=raw,null_handle=null_handle,null_out=null_out)
     o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,state=o))
result=dict(status='PASS',fresh_cases=len(rows),ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),
 source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),cases=rows,
 limits=['Null handle read and null output write stop at unmapped-memory hook before exception delivery.','Synthetic UART IRQ registers; no physical status measurement.'])
(D/'codec-irq-status-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'codec IRQ status original/source cases')
