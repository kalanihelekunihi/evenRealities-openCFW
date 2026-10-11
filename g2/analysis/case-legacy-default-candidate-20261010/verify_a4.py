#!/usr/bin/env python3
"""Stock/source version branch with controlled logger and source-owned text."""
from pathlib import Path
import hashlib,json,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:];elf=D/'a4.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def readz(u,p):
 b=bytearray()
 while len(b)<64:
  c=u.mem_read(p+len(b),1)[0]
  if not c:break
  b.append(c)
 return b.decode()
rows=[]
for length,flag,counter,logger_return,mutate in itertools.product([0,1,2,8],[0,1,0x7f],[0,1,0x12345678],[0,0xabcdef01],[False,True]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_write(0x20004000,bytes([0xa4,0x55])+bytes(30));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x20000888,counter.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[];writes=[]
  def code(uc,address,size,user):
   if address in [0x08009170,0x0010f200]:
    fmt=readz(uc,uc.reg_read(UC_ARM_REG_R0));arg1=uc.reg_read(UC_ARM_REG_R1) if '%d' in fmt else None;arg2=None
    events.append([fmt,arg1,arg2]);uc.reg_write(UC_ARM_REG_R0,logger_return)
    if mutate and len(events)==2 and flag==0:uc.mem_write(0x200000bf,b'\x01')
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def write(uc,access,address,size,value,user):
   if not 0x20007fc0<=address<0x20008000:writes.append([address,size,value])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x08000928 if original else sym['case_legacy_a4_branch'])|1,0x20001000,count=10000)
  pair.append(dict(return_value=u.reg_read(UC_ARM_REG_R0),events=events,writes=writes,flag=bytes(u.mem_read(0x200000bf,1)).hex()))
 assert pair[0]==pair[1],(length,flag,counter,logger_return,mutate,pair)
 rows.append(dict(length=length,flag=flag,counter=counter,logger_return=logger_return,mutate=mutate,comparison=pair[0]))
out=dict(status='PASS_A4_BOUNDED_BRANCH',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/word_a4.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Only opcode 0xa4; lower logger is controlled and may mutate the flag after the second call.','No public legacy provider, formatter/UART or physical CASE claim.'],rows=rows)
(D/'a4-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
