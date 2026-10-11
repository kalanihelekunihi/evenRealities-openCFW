#!/usr/bin/env python3
"""Original/source INFO selector and revision RAM comparisons."""
import hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/info_read_revision_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-info-read-revision.ld');ELF=Path('/tmp/audio-info-read-revision.elf')
LD.write_text('audio_info_space_read = 0x4d3ddb; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,kind,space=1,offset=0x244,count=1,revision=0xffffffff,child_status=0,child_word=0x12345678,nonnull=True):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000)
 u.mem_write(0x200001e8,struct.pack('<I',revision));u.mem_write(0x20010000,b'\xA5'*16)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301)
 if kind=='info':
  for reg,val in ((UC_ARM_REG_R0,space),(UC_ARM_REG_R1,offset),(UC_ARM_REG_R2,count),(UC_ARM_REG_R3,0x20010000)):u.reg_write(reg,val)
  start=0x4d3f3d if not native else symbol['stock_info_read']|1
 else:
  u.reg_write(UC_ARM_REG_R0,0x20010000 if nonnull else 0)
  start=0x47ef39 if not native else symbol['stock_revision']|1
 calls=[];writes=[]
 def hook(cpu,addr,_size,_):
  if addr==0x4d3dda:
   args=[cpu.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   calls.append(args)
   cpu.mem_write(args[3],struct.pack('<I',child_word))
   cpu.reg_write(UC_ARM_REG_R0,child_status);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
 def write(_cpu,_access,addr,size,value,_):
  if addr<0x2007d000:writes.append([addr,size,value])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start(start,0x100300,count=300)
 return dict(result=u.reg_read(UC_ARM_REG_R0),revision=struct.unpack('<I',u.mem_read(0x200001e8,4))[0],out=u.mem_read(0x20010000,16).hex(),calls=calls,writes=writes,sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

rows=[]
for space in (0,1,2,3,4,5,6,0x101,0x103,0x105,0xffffffff):
 for status in (0,7):
  c=dict(kind='info',space=space,child_status=status)
  a,b=run(False,**c),run(True,**c);assert a==b,(c,a,b);rows.append(dict(inputs=c,state=a))
for rev in (0,1,0x12345678,0xffffffff):
 for status in (0,7):
  for word in (0,0x12345678):
   for valid in (True,False):
    c=dict(kind='revision',revision=rev,child_status=status,child_word=word,nonnull=valid)
    a,b=run(False,**c),run(True,**c);assert a==b,(c,a,b);rows.append(dict(inputs=c,state=a))
result=dict(status='PASS',fresh_cases=len(rows),info_cases=22,revision_cases=32,
 ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
 gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),
 link_script=LD.read_text(),cases=rows,limits=['INFO child 0x4D3DDA is a controlled provider boundary: arguments and destination writes are compared, but its implementation remains unresolved.','Synthetic RAM; no flash/OTP hardware read or live boot revision.'])
(D/'info-read-revision-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'INFO selector/revision original-source cases')
