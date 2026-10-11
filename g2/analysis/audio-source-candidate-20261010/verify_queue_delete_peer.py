#!/usr/bin/env python3
"""Original/source CMSIS queue-delete wrapper with real kernel children."""
import hashlib,json,struct,subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
OTA=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SRC=R/'g2/components/audio/source_candidate_20261010/queue_delete_peer_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LD=Path('/tmp/audio-queue-delete-peer.ld');ELF=Path('/tmp/audio-queue-delete-peer.elf')
LD.write_text('audio_irq_context = 0x44900f; audio_queue_delete = 0x441ea3; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-T',str(LD),str(SRC),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);syms=e.get_section_by_name('.symtab');symbol={s.name:s['st_value'] for s in syms.iter_symbols()};compiled=e.get_section_by_name('.text').data()

def run(native,static,ipsr,null,primask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x1000);u.mem_write(0x100000,compiled)
 u.mem_map(0x20000000,0x80000);u.mem_map(0xe000e000,0x2000)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 B=0x20006000;Q=B+8;END=B+256;START=0x20074158
 w(B,0,0x80000080);u.mem_write(Q+0x46,bytes([static]));w(END,0,0)
 w(START,END,0);w(0x2007465c,END);w(0x20074660,0);w(0x2007466c,7)
 w(0x20074a30,0);w(0x20074a3c,1);w(0x20074a58,0)
 u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask)
 u.reg_write(UC_ARM_REG_R0,0 if null else Q);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100301)
 u.emu_start((symbol['audio_queue_delete_peer']|1) if native else 0x449bed,0x100300,count=20000)
 return dict(result=u.reg_read(UC_ARM_REG_R0),block=u.mem_read(B,0x100).hex(),
  freelist=u.mem_read(START,8).hex(),heap=u.mem_read(0x2007465c,20).hex(),
  primask=u.reg_read(UC_ARM_REG_PRIMASK),basepri=u.reg_read(UC_ARM_REG_BASEPRI),
  sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

rows=[]
for static in (0,1):
 for ipsr in (0,15):
  for null in (False,True):
   for primask in (0,1):
    c=dict(static=static,ipsr=ipsr,null=null,primask=primask)
    o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,state=o))
result=dict(status='PASS',fresh_cases=len(rows),ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),
 source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),cases=rows,
 limits=['Actual original IRQ-context and queue-delete/free children execute; prior independent source suites cover those bodies. Synthetic coherent isolated heap and scheduler-unstarted state, no live queue users.'])
(D/'queue-delete-peer-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'queue-delete-peer original/source cases')
