#!/usr/bin/env python3
"""Linked stock/source binary 0x51 and 0x5f through flash-copy wrappers."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_linked_entry.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for op,length,flag,variant in itertools.product([0x51,0x5f],[0,1,20],[0,1,0x7f],[0,1,2,3]):
 size=8 if op==0x51 else 16;addr=0x0803f800 if op==0x51 else 0x0803f000;data=[bytes(size),bytes(range(size)),bytes([0xff])*size,bytes((i*17+3)&255 for i in range(size))][variant]
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,raw);u.mem_write(addr,data);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x20000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([op,0,2])+bytes(253));u.mem_write(0x200000bf,bytes([flag]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];stop=[False]
  def hook(uc,a,sz,_):
   if a in [0x0800680c,sym['case_binary_send51']&~1,sym['case_binary_send5f']&~1]:
    p=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);ev.append(['send',n,bytes(uc.mem_read(p,n)).hex()]);stop[0]=True;uc.emu_stop()
   elif a==0x08009170:raise AssertionError('unexpected logger')
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000e1c if original else sym['case_binary_linked_entry'])|1,0x20001000,count=10000)
  assert stop[0],(op,length,flag,variant,original,ev)
  pair.append([ev,bytes(u.mem_read(0x200000bf,1)).hex()])
 assert pair[0]==pair[1],(op,length,flag,variant,pair)
 rows.append([op,length,flag,variant,data.hex(),pair[0]])
out=dict(status='PASS_BINARY_LINKED_FLASH_FILL',cases=len(rows),image_sha256=sha,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Synthetic flash data at 0x0803f800 and 0x0803f000; pinned CASE image does not contain those bytes.','Stops at send; physical flash bus and UART effects excluded.','Test linked entry only, no selected public handler.'],rows=rows)
(D/'binary-linked-flash-fill.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
