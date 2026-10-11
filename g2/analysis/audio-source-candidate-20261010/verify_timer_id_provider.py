#!/usr/bin/env python3
"""Bounded original/source Apollo timer ID getter comparison."""
import hashlib, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[3]
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
ELF=Path('/tmp/audio-timer-id.elf')
SOURCE=ROOT/'g2/components/audio/source_candidate_20261010/timer_id_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LINK=Path('/tmp/audio-timer-id.ld')
LINK.write_text('stock_enter_critical = 0x4420d1; stock_exit_critical = 0x4420e9; audio_port_mask_set = 0x5fa0a5;\nSECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LINK),str(SOURCE),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f); section=e.get_section_by_name('.text'); compiled=section.data()

def run(native,ident,depth,mask,null=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000)
 timer=0x20010000
 u.mem_write(timer,bytes([0xA5])*44);u.mem_write(timer+28,struct.pack('<I',ident))
 u.mem_write(0x2000309c,struct.pack('<I',depth))
 u.reg_write(UC_ARM_REG_BASEPRI,mask);u.reg_write(UC_ARM_REG_SP,0x2007e000)
 u.reg_write(UC_ARM_REG_LR,0x100101);u.reg_write(UC_ARM_REG_R0,0 if null else timer)
 trace=[];last=[mask];end=[]
 def code(cpu,addr,_size,_):
  m=cpu.reg_read(UC_ARM_REG_BASEPRI)
  if m!=last[0]:trace.append(['basepri',m]);last[0]=m
  if null and addr in (0x47eb3a,0x100020):
   end.append('fault_loop');cpu.emu_stop()
 def write(_cpu,_access,addr,size,value,_):
  if addr<0x2007d000:trace.append(['write',addr,size,value])
 def invalid_write(cpu,_access,addr,size,value,_):
  trace.append(['invalid_write',addr,size,value]);end.append('invalid_write');cpu.emu_stop();return True
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,invalid_write)
 try:u.emu_start(0x47eb27 if not native else 0x100001,0x100100,count=200)
 except UcError:
  if not (null and end==['invalid_write']):raise
 return dict(result=u.reg_read(UC_ARM_REG_R0) if not null else None,
             nesting=struct.unpack('<I',u.mem_read(0x2000309c,4))[0],
             basepri=u.reg_read(UC_ARM_REG_BASEPRI),
             timer_hex=u.mem_read(timer,44).hex(),sp=u.reg_read(UC_ARM_REG_SP),
             trace=trace,end=end,pc=u.reg_read(UC_ARM_REG_PC))

rows=[]
for ident in (0,1,0x12345678,0xffffffff):
 for depth in (0,1,2):
  for mask in (0,0x20,0x30,0x80):
   o=run(False,ident,depth,mask);n=run(True,ident,depth,mask)
   assert o==n,(ident,depth,mask,o,n)
   assert o['result']==ident and o['nesting']==depth and o['timer_hex'][56:64]==struct.pack('<I',ident).hex()
   rows.append(dict(id=ident,critical_depth=depth,initial_basepri=mask,state=o))
for mask in (0,0x30):
 o=run(False,0,1,mask,True);n=run(True,0,1,mask,True)
 assert {k:v for k,v in o.items() if k not in ('pc',)}=={k:v for k,v in n.items() if k not in ('pc',)},(o,n)
 assert o['end']==['invalid_write'] and o['trace'][-1]==['invalid_write',0xffffffff,4,0]
 rows.append(dict(null=True,initial_basepri=mask,original=o,source=n))
result=dict(status='PASS',fresh_cases=len(rows),nonnull_cases=len(rows)-2,null_fatal_prefix_cases=2,
 ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),link_script=LINK.read_text(),cases=rows,
 limits=['Null comparison executes the original mask helper 0x5FA0A4 and compares the attempted invalid-address write, stopping on the unmapped-memory hook before fault delivery/endless loop.','Synthetic Cortex-M4 critical state; no live interrupt scheduling or physical timer lifetime.'])
Path(__file__).with_name('timer-id-provider-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'timer ID original/source cases')
