#!/usr/bin/env python3
"""Stock/source linked binary 0x56 through exit child to ack."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_linked_entry.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def z(u,p):
 b=bytearray()
 while len(b)<80:
  v=u.mem_read(p+len(b),1)[0]
  if not v:break
  b.append(v)
 return b.decode()
rows=[]
for length,b4,b5,flag,childret in itertools.product([0,5,6,20],[0,1,2],[0,1,2],[0,1,0x7f],[0,0x98765432]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([0x56,0,2,0,b4,b5])+bytes(250));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x200000d0,(0x12345678).to_bytes(4,'little'));u.mem_write(0x20000895,bytes([0x44,0x55]));u.mem_write(0x2000087e,b'\xa5');u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];writes=[];stop=[False]
  def hook(uc,a,size,_):
   if a in [0x08009170,0x0010f1c0,0x0010f480]:
    ev.append(['log',z(uc,uc.reg_read(UC_ARM_REG_R0))]);uc.reg_write(UC_ARM_REG_R0,0x1234);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x0800ab26,0x0010f420]:
    ev.append(['cancel',uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,childret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08006b80,0x0010f440]:
    ev.append(['clear_a',uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,childret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08006b98,0x0010f460]:
    ev.append(['clear_b',uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,childret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x080068d0,0x0010f180]:
    ev.append(['ack',uc.reg_read(UC_ARM_REG_R0)]);stop[0]=True;uc.emu_stop()
  def wr(uc,access,a,n,v,_):
   if a in [0x20000895,0x20000896,0x2000087e]:writes.append([a,n,v])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start((0x08000e1c if original else sym['case_binary_56_candidate'])|1,0x20001000,count=10000)
  assert stop[0] or u.reg_read(UC_ARM_REG_PC)==0x20001000,(length,b4,b5,flag,original,ev)
  pair.append([ev,writes,bytes(u.mem_read(0x20000895,2)).hex(),bytes(u.mem_read(0x2000087e,1)).hex(),bytes(u.mem_read(0x200000bf,1)).hex(),None if stop[0] else u.reg_read(UC_ARM_REG_R0)])
 assert pair[0]==pair[1],(length,b4,b5,flag,childret,pair)
 rows.append([length,b4,b5,flag,childret,pair[0]])
out=dict(status='PASS_BINARY_LINKED_56_EXIT',cases=len(rows),image_sha256=sha,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Destination byte 2; opcode 56; allocated 256-byte input.','Exit wrapper executes; task cancellation, GPIO, logger and ack controlled.','Linked branch, not full case_binary_command.'],rows=rows)
(D/'binary-linked-56-exit-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
