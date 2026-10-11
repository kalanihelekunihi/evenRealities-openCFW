#!/usr/bin/env python3
"""Apollo original/source power-status wrapper with real descriptor bodies."""
import hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/peripheral_enabled_provider.c'
DESC=R/'g2/components/foundation/power_domain/power_domain.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-peripheral-enabled.ld');ELF=Path('/tmp/audio-peripheral-enabled.elf')
LD.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),str(DESC),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,domain,nonnull,reg_word):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x3000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000);u.mem_map(0x40020000,0x3000)
 for a in (0x40021008,0x40021010):u.mem_write(a,struct.pack('<I',reg_word))
 out=0x20010000;u.mem_write(out,b'\xA5'*4)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301)
 u.reg_write(UC_ARM_REG_R0,domain);u.reg_write(UC_ARM_REG_R1,out if nonnull else 0)
 writes=[]
 def write(_cpu,_access,addr,size,value,_):
  if addr<0x2007d000:writes.append([addr,size,value])
 u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((symbol['stock_peripheral_enabled']|1) if native else 0x47f90d,0x100300,count=500)
 return dict(result=u.reg_read(UC_ARM_REG_R0),out=u.mem_read(out,4).hex(),writes=writes,sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

rows=[]
for domain in (0,1,7,11,15,28,29,30,31,32,33,34,255,256,285):
 for nonnull in (True,False):
  for word in (0,0xffffffff,0x00000040):
   c=dict(domain=domain,nonnull=nonnull,reg_word=word)
   o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n)
   rows.append(dict(inputs=c,state=o))
result=dict(status='PASS',fresh_cases=len(rows),ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),
 source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),descriptor_source_sha256=hashlib.sha256(DESC.read_bytes()).hexdigest(),
 gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),
 cases=rows,limits=['Real original/source descriptor bodies with synthetic power-status registers; no physical power-state transition or device measurement.'])
(D/'peripheral-enabled-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'peripheral enabled original/source cases')
