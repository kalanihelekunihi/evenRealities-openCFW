#!/usr/bin/env python3
"""Original/source task notification state clear and critical effects."""
import hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_MEM_WRITE_UNMAPPED, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/receiver_state_clear_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-receiver-state-clear.ld');ELF=Path('/tmp/audio-receiver-state-clear.elf')
LD.write_text('audio_port_mask_set = 0x5fa0a5; stock_enter_critical = 0x4420d1; stock_exit_critical = 0x4420e9; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,state,depth,mask,null,index):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000)
 task=0x20010000;u.mem_write(task,bytes([0xa5])*0x80);u.mem_write(task+0x6c,bytes([state]))
 u.mem_write(0x20074a20,struct.pack('<I',task));u.mem_write(0x2000309c,struct.pack('<I',depth))
 u.reg_write(UC_ARM_REG_BASEPRI,mask);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301)
 u.reg_write(UC_ARM_REG_R0,0 if null else task);u.reg_write(UC_ARM_REG_R1,index)
 writes=[];fault=[]
 def write(_cpu,_access,addr,size,value,_):
  if addr<0x2007d000:writes.append([addr,size,value])
 def bad(cpu,_access,addr,size,value,_):
  fault.append([addr,size,value]);cpu.emu_stop();return True
 u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,bad)
 try:u.emu_start((symbol['receiver_state_clear']|1) if native else 0x455f5f,0x100300,count=150)
 except UcError:
  if not fault:raise
 return dict(result=None if fault else u.reg_read(UC_ARM_REG_R0),fault=fault,
  task=u.mem_read(task,0x80).hex(),nesting=struct.unpack('<I',u.mem_read(0x2000309c,4))[0],
  basepri=u.reg_read(UC_ARM_REG_BASEPRI),writes=writes,sp=u.reg_read(UC_ARM_REG_SP),pc=None if fault else u.reg_read(UC_ARM_REG_PC))

rows=[]
for state in (0,1,2,3,255):
 for depth in (0,1,2):
  for mask in (0,0x30):
   for null in (False,True):
    c=dict(state=state,depth=depth,mask=mask,null=null,index=0)
    o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,state=o))
for index in (1,0xffffffff):
 c=dict(state=2,depth=1,mask=0,null=False,index=index)
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,state=o))
result=dict(status='PASS',fresh_cases=len(rows),nonnull_index_cases=60,invalid_index_fault_cases=2,
 ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
 gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),
 cases=rows,limits=['Critical/mask original child bodies execute; invalid index comparison stops at attempted write to unmapped 0xFFFFFFFF before exception delivery.','Synthetic task control block and critical state, no live scheduling.'])
(D/'receiver-state-clear-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'receiver state clear original/source cases')
