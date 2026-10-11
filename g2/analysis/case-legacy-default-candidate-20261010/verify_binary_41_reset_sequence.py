#!/usr/bin/env python3
"""Stock/source ff reset sequence through first repeated idle loop."""
from pathlib import Path
import hashlib,json,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:];elf=D/'binary_41_reset.elf'
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
for length,flag,logger_return,ack_return in itertools.product([0,1,5,20],[0,1,0x7f],[0,0x12345678],[0,0x76543210]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000);u.mem_map(0xe000e000,0x1000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_write(0x20004000,bytes([0x41,0,2,0,0])+bytes(27));u.mem_write(0x200000bf,bytes([flag]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[];writes=[];stopped=[False];visits=[0]
  def code(uc,address,size,user):
   if address in [0x080068d0,0x0010f000]:
    events.append(['ack',uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,ack_return);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if address in [0x08009170,0x0010f100]:
    events.append(['log',readz(uc,uc.reg_read(UC_ARM_REG_R0))]);uc.reg_write(UC_ARM_REG_R0,logger_return);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if address in [0x0800502c,(sym['case_legacy_reset_first'] & ~1)]:
    events.append(['enter_reset_child',uc.reg_read(UC_ARM_REG_R0)])
   if address in [0x0800503a,(sym['case_legacy_reset_first'] & ~1)+14]:
    visits[0]+=1
    if visits[0]==2:
     events.append(['reset_loop_revisited']);stopped[0]=True;uc.emu_stop()
  def write(uc,access,address,size,value,user):
   if address==0xe000ed0c:writes.append([address,size,value])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x08000e1c if original else sym['case_binary_06_41_candidate'])|1,0x20001000,count=10000)
  pair.append(dict(events=events,writes=writes,flag=bytes(u.mem_read(0x200000bf,1)).hex(),stopped=stopped[0]))
 assert pair[0]==pair[1],(length,flag,logger_return,ack_return,pair)
 rows.append(dict(length=length,flag=flag,logger_return=logger_return,ack_return=ack_return,comparison=pair[0]))
out=dict(status='PASS_BINARY_41_RESET_SEQUENCE',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_06_41_candidate.c').read_bytes()+(root/'g2/components/case/legacy_default_candidate_20261010/reset_ff_prefix.c').read_bytes()+(root/'g2/components/case/legacy_default_candidate_20261010/reset_child_502c.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Stops at second visit of reset child idle loop after observing AIRCR write.','M0 emulator does not model physical reset from AIRCR; no device reset or public handler claim.'],rows=rows)
(D/'binary-41-reset-sequence-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
