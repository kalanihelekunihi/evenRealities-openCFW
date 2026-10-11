#!/usr/bin/env python3
"""GX8002 RX FIFO original/source comparison with synthetic MMIO reads."""
import hashlib, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_READ
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[3]
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE=ROOT/'g2/components/audio/source_candidate_20261010/codec_fifo_read_provider.c'
GCC=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
LINK=Path('/tmp/audio-codec-fifo-read.ld');ELF=Path('/tmp/audio-codec-fifo-read.elf')
LINK.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run([str(GCC),'-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib',
                '-T',str(LINK),str(SOURCE),'-o',str(ELF)],check=True)
raw=OTA.read_bytes()[32:]
with ELF.open('rb') as f:
 e=ELFFile(f);code=e.get_section_by_name('.text').data()
 symbol=next(s for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='codec_fifo_read')
 source_entry=symbol['st_value']|1

def run(original,instance,length,buffer_present,count_present,ready,data):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
 u.mem_map(0x100000,0x2000);u.mem_write(0x100000,code)
 u.mem_map(0x20000000,0x80000);u.mem_map(0x40039000,0x4000)
 handle=0x20010000;buffer=0x20011000;countptr=0x20012000
 u.mem_write(handle,bytes([0xa5])*44);u.mem_write(handle+40,struct.pack('<I',instance))
 u.mem_write(buffer,bytes([0xcc])*12);u.mem_write(countptr,struct.pack('<I',0xdeadbeef))
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x100801)
 for reg,val in ((UC_ARM_REG_R0,handle),(UC_ARM_REG_R1,buffer if buffer_present else 0),
                 (UC_ARM_REG_R2,length),(UC_ARM_REG_R3,countptr if count_present else 0)):u.reg_write(reg,val)
 base=0x40039000+(instance<<12);trace=[];ri=[0];di=[0];done=[False]
 def code_hook(cpu,addr,_size,_):
  if addr==0x100800:done[0]=True;cpu.emu_stop()
 def read_hook(cpu,_access,addr,size,_value,_):
  if addr==base+24:
   assert ri[0]<len(ready),('extra status read',trace)
   val=16 if ready[ri[0]] else 0;ri[0]+=1;cpu.mem_write(addr,struct.pack('<I',val));trace.append(['status',addr,val])
  elif addr==base:
   assert di[0]<len(data),('extra data read',trace)
   val=data[di[0]];di[0]+=1;cpu.mem_write(addr,struct.pack('<I',val));trace.append(['data',addr,val])
 u.hook_add(UC_HOOK_CODE,code_hook);u.hook_add(UC_HOOK_MEM_READ,read_hook)
 u.emu_start(0x58e2d9 if original else source_entry,0x100900,count=200)
 assert done[0] and ri[0]==len(ready) and di[0]==len(data),(trace,done,ri,di)
 return dict(result=u.reg_read(UC_ARM_REG_R0),buffer=u.mem_read(buffer,12).hex(),
             count=u.mem_read(countptr,4).hex(),handle=u.mem_read(handle,44).hex(),
             trace=trace,sp=u.reg_read(UC_ARM_REG_SP),pc=u.reg_read(UC_ARM_REG_PC))

cases=[]
scenarios=[(0,[],[]),(3,[1],[]),(1,[0],[0x12]),(2,[0,0],[0x12,0x34]),
           (3,[0,0,0],[0x12,0x34,0x56]),(3,[0,0,1],[0x12,0x34]),
           (3,[0],[0x100]),(3,[0,0],[0x42,0x800]),(3,[0,0],[0x42,0xf00]),
           (1,[0,1],[0x72])]
for instance in (0,1,3):
 for length,ready,data in scenarios:
  for buffer_present in (True,False):
   if buffer_present and length==1 and ready==[0,1]:continue
   if not buffer_present and length and ready and ready[0]==0:
    if (len(ready)!=2 or ready[-1]!=1):continue
   for count_present in (True,False):
    old=run(True,instance,length,buffer_present,count_present,ready,data)
    new=run(False,instance,length,buffer_present,count_present,ready,data)
    assert old==new,(instance,length,buffer_present,count_present,ready,data,old,new)
    cases.append(dict(instance=instance,length=length,buffer_present=buffer_present,
                      count_present=count_present,ready=ready,data=data,state=old))
result=dict(status='PASS',fresh_cases=len(cases),original_entry='0x58e2d8',
 ota_sha256=hashlib.sha256(OTA.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),gcc_sha256=hashlib.sha256(GCC.read_bytes()).hexdigest(),
 link_script=LINK.read_text(),cases=cases,
 limits=['Synthetic MMIO read sequence, no live codec or interrupt delivery.',
         'Nonnull valid handle only; null/invalid instance and unbounded null-buffer FIFO loops are outside this fixture.'])
Path(__file__).with_name('codec-fifo-read-execution.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(cases),'codec FIFO original/source cases')
