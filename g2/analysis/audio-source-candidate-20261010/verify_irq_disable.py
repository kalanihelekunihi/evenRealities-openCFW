#!/usr/bin/env python3
"""Original/source NVIC disable register and barrier path comparison."""
import hashlib,json,subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/irq_disable_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-irq-disable.ld');ELF=Path('/tmp/audio-irq-disable.elf')
LD.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,irq,old):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000);u.mem_map(0xe000e000,0x2000)
 u.mem_write(0xe000e180,old.to_bytes(4,'little'))
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301);u.reg_write(UC_ARM_REG_R0,irq&0xffffffff)
 writes=[]
 def write(_cpu,_access,addr,size,value,_):writes.append([addr,size,value])
 u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((symbol['audio_irq_disable']|1) if native else 0x57a48b,0x100300,count=100)
 return dict(writes=writes,icer0=u.mem_read(0xe000e180,4).hex(),sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

rows=[]
for irq in (-32768,-129,-32,-1,0,1,15,31,32,33,63,64,127,239,255,32767,65536,65568,0xffffffff):
 for old in (0,0xa5a5a5a5):
  c=dict(irq=irq,old=old);o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n)
  rows.append(dict(inputs=c,state=o))
result=dict(status='PASS',fresh_cases=len(rows),ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),
 source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),cases=rows,
 limits=['Synthetic NVIC ICER memory; architecture barrier instructions execute in emulator but interrupt delivery or peripheral IRQ state is not measured.'])
(D/'irq-disable-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'IRQ disable original/source cases')
