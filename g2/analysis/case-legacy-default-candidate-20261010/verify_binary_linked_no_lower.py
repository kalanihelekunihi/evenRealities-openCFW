#!/usr/bin/env python3
"""Authenticated stock/source linked binary composition on no-lower cases."""
from pathlib import Path
import hashlib,json,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_linked_entry.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stubs={v&~1 for k,v in sym.items() if k.startswith('case_binary_') and 0x0010f000<=v<0x00110000}
special={0x06,0x14,0x3e,0x3f,0x41,0x50,0x51,0x56,0x5c,0x5d,0x5e,0x5f,0x68}
cases=[]
for op in range(256):
 for dest in [0,1,3]:
  for n,mode in itertools.product([0,1,4],[0,1]):cases.append((op,dest,n,mode,1))
 if op not in special:
  for n in [0,5,20]:cases.append((op,2,n,0,1))
for op in [0x3e,0x3f,0x56,0x5d,0x68]:
 for n,flag in itertools.product([0,1,4],[0,1]):cases.append((op,2,n,0,flag))
for n in [0,1,4]:cases.append((0x5e,2,n,0,1))
rows=[]
for op,dest,n,mode,flag in cases:
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x20000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([op,0,dest,0,0])+bytes(251));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x200000f5,b'\x00');u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_R2,mode);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  hit=[]
  def hook(uc,a,size,_):
   if a in stubs or a in [0x08009170,0x0800a888,0x080001b4,0x0800680c,0x080068d0]:hit.append(hex(a));uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000e1c if original else sym['case_binary_linked_entry'])|1,0x20001000,count=10000)
  assert not hit and u.reg_read(UC_ARM_REG_PC)==0x20001000,(op,dest,n,mode,flag,original,hit,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append([u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200000bf,1)).hex(),bytes(u.mem_read(0x200000f0,16)).hex(),bytes(u.mem_read(0x20000880,32)).hex()])
 assert pair[0]==pair[1],(op,dest,n,mode,flag,pair)
 rows.append([op,dest,n,mode,flag,pair[0]])
out=dict(status='PASS_BINARY_LINKED_NO_LOWER',cases=len(rows),image_sha256=sha,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['No lower calls are allowed in this corpus; excludes every path reaching controlled send/ack/control/logger/dispatch.','Input allocation 256 bytes at every logical length.','Linked source test ELF only, not public provider or selected archive.'],rows=rows)
(D/'binary-linked-no-lower.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
