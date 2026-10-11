#!/usr/bin/env python3
"""Stock/source 0xa3 producer/status reporting with explicit lower calls."""
from pathlib import Path
import hashlib,json,itertools,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:];elf=D/'a3.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def readz(u,p):
 b=bytearray()
 while len(b)<160:
  c=u.mem_read(p+len(b),1)[0]
  if not c:break
  b.append(c)
 return b.decode()
rows=[];pairs=[(0,0,0),(0x12345678,0x87654321,0xffffffff)]
for length,flag,values,mutate,logger_return in itertools.product([0,1,2,8],[0,1,0x7f],pairs,[False,True],[0,0xabcdef01]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_write(0x20004000,bytes([0xa3,0x55])+bytes(30));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087c,bytes([0,11,0,33,44]+[0]*11+[66,77]+[0]*14));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[];writes=[]
  def code(uc,address,size,user):
   child={0x08009ff0:0,0x08009f18:1,0x0800a01e:2,0x0010f500:0,0x0010f600:1,0x0010f700:2}
   if address in child:
    i=child[address];uc.mem_write(uc.reg_read(UC_ARM_REG_R0),values[i].to_bytes(4,'little'));events.append(['value',i,values[i]]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if address in [0x08009170,0x0010f200]:
    fmt=readz(uc,uc.reg_read(UC_ARM_REG_R0));args=[]
    if '%d' in fmt:
     args=[uc.reg_read(r) for r in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
     args+=list(struct.unpack('<5I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),20))))
    events.append(['log',fmt,args]);uc.reg_write(UC_ARM_REG_R0,logger_return)
    if mutate and len([e for e in events if e[0]=='log'])==2 and flag==0:uc.mem_write(0x200000bf,b'\x01')
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def write(uc,access,address,size,value,user):
   if not 0x20007fc0<=address<0x20008000:writes.append([address,size,value])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x08000928 if original else sym['case_legacy_a3_branch'])|1,0x20001000,count=20000)
  pair.append(dict(return_value=u.reg_read(UC_ARM_REG_R0),events=events,writes=writes,flag=bytes(u.mem_read(0x200000bf,1)).hex()))
 assert pair[0]==pair[1],(length,flag,values,mutate,logger_return,pair)
 rows.append(dict(length=length,flag=flag,values=values,mutate=mutate,logger_return=logger_return,comparison=pair[0]))
out=dict(status='PASS_A3_BOUNDED_BRANCH',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/status_a3.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Only opcode 0xa3. Three producers and logger are controlled ABI cuts.','No public legacy handler, physical CASE, formatter or UART claim.'],rows=rows)
(D/'a3-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
