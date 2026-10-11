#!/usr/bin/env python3
"""Compare original/source trace-disable wrapper with bounded wait boundary."""
import hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/trace_disable_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-trace-disable.ld');ELF=Path('/tmp/audio-trace-disable.elf')
LD.write_text('stock_save_irq = 0x473941; stock_wait_status = 0x4807fd; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,users,mask,demcr,wait_status):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000);u.mem_map(0xe000e000,0x2000)
 u.mem_write(0x20074f5e,bytes([users]));u.mem_write(0xe000edfc,struct.pack('<I',demcr))
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 writes=[];calls=[]
 def code(cpu,addr,_size,_):
  if addr==0x4807fc:
   calls.append([cpu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)])
   cpu.reg_write(UC_ARM_REG_R0,wait_status);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
 def write(_cpu,_access,addr,size,value,_):
  if addr in (0x20074f5e,0xe000edfc):writes.append([addr,size,value])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((symbol['stock_trace_disable']|1) if native else 0x4d403f,0x100300,count=150)
 return dict(result=u.reg_read(UC_ARM_REG_R0),users=u.mem_read(0x20074f5e,1).hex(),
  demcr=struct.unpack('<I',u.mem_read(0xe000edfc,4))[0],mask=u.reg_read(UC_ARM_REG_PRIMASK),
  calls=calls,writes=writes,sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

rows=[]
for users in (0,1,2,3,255):
 for mask in (0,1):
  for demcr in (0,0x01000000):
   for wait_status in (0,3,7):
    c=dict(users=users,mask=mask,demcr=demcr,wait_status=wait_status)
    o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,state=o))
result=dict(status='PASS',fresh_cases=len(rows),ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),
 source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),cases=rows,
 limits=['Save-IRQ child executes original body; wait4 is a controlled boundary with compared four arguments and synthetic status. Its independent source suite remains separate.','Synthetic DEMCR and nesting byte; no physical trace-clock/interrupt timing.'])
(D/'trace-disable-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'trace-disable original/source cases')
