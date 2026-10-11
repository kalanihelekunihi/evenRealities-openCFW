#!/usr/bin/env python3
"""Stock/source 0xdf log-toggle branch with source-owned strings."""
from pathlib import Path
import hashlib,json,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:];elf=D/'df.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for length,byte,flag,lower_return in itertools.product([0,1,2,8],[0,1,2,0x7f,0xff],[0,1,0x7f],[0,0x12345678]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_write(0x20004000,bytes([0xdf,byte])+bytes(30));u.mem_write(0x200000be,b'\x5a');u.mem_write(0x200000bf,bytes([flag]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[];writes=[]
  def code(uc,address,size,user):
   if address in [0x08009170,0x0010f200]:
    p=uc.reg_read(UC_ARM_REG_R0);s=bytearray()
    while len(s)<64:
     c=uc.mem_read(p+len(s),1)[0]
     if not c:break
     s.append(c)
    
    arg=None
    if s==b'%s dog feed':
     q=uc.reg_read(UC_ARM_REG_R1);b=bytearray()
     while len(b)<64:
      c=uc.mem_read(q+len(b),1)[0]
      if not c:break
      b.append(c)
     arg=b.decode()
    events.append([s.decode(),arg]);uc.reg_write(UC_ARM_REG_R0,lower_return);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def write(uc,access,address,size,value,user):
   if not 0x20007fc0<=address<0x20008000:writes.append([address,size,value])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x08000928 if original else sym['case_legacy_df_branch'])|1,0x20001000,count=10000)
  pair.append(dict(return_value=u.reg_read(UC_ARM_REG_R0),events=events,writes=writes,flag=bytes(u.mem_read(0x200000bf,1)).hex()+bytes(u.mem_read(0x200000be,1)).hex()))
 assert pair[0]==pair[1],(length,byte,flag,lower_return,pair)
 rows.append(dict(length=length,byte=byte,flag=flag,lower_return=lower_return,comparison=pair[0]))
out=dict(status='PASS_DF_BOUNDED_BRANCH',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/dogfeed_df.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Only opcode 0xdf; logger is an explicit controlled ABI cut.','No full legacy command provider, formatter, UART or physical CASE claim.'],rows=rows)
(D/'df-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
