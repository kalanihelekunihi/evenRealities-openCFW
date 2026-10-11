#!/usr/bin/env python3
"""Stock/source linked binary 3d and forward paths through shared copy body."""
from pathlib import Path
import hashlib,itertools,json,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_linked_entry.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
assert sym['case_binary_3d_dispatch']==sym['case_binary_forward_dispatch']
def z(u,p):
 b=bytearray()
 while len(b)<80:
  v=u.mem_read(p+len(b),1)[0]
  if not v:break
  b.append(v)
 return b.decode()
rows=[]
for op,dest,mode,length,active,flag in itertools.product([0x3d,0x55],[0,1,3],[0,1],[4,5,6,7],[0,1],[0,1]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  frame=bytes([op,0,dest,0,0,0x89,0xab])+bytes(249)
  u.mem_write(0x20004000,frame);u.mem_write(0x200001b4,b'\xa5'*16)
  u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x200000f0,struct.pack('<I',0x20005000));u.mem_write(0x200000f5,bytes([active]))
  u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,mode);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[]
  def hook(uc,a,size,_):
   if a in [0x0800a888,0x0010f060,0x0010f280]:
    events.append(['control',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);uc.reg_write(UC_ARM_REG_R0,0x9876);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08009170,0x0010f0a0]:
    events.append(['log',z(uc,uc.reg_read(UC_ARM_REG_R0))]);uc.reg_write(UC_ARM_REG_R0,0x1234);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08000e1c if original else sym['case_binary_linked_entry'])|1,0x20001000,count=20000)
  row=[events,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200001b4,16)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(op,dest,mode,length,active,flag,pair)
 rows.append([op,dest,mode,length,active,flag,pair[0]])
out=dict(status='PASS_BINARY_LINKED_DISPATCH_COPY',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Two opcode representatives, destinations 0/1/3, modes 0/1 and lengths 4-7; accepted/rejected frame branches.','Control and logger controlled; copy body executes and state bytes/R0 compared.','No physical transport or public handler admission.'],rows=rows)
(D/'binary-linked-dispatch-copy-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
