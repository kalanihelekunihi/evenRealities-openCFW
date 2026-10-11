#!/usr/bin/env python3
"""Authenticated stock/source four binary local routes with logging enabled."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_linked_entry.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for op,n,p4,p5,status,flag in itertools.product([0x50,0x5c,0x5d,0x68],[0,4,5,6,20],[0,1],[0,1],[0,1],[0,1,0x7f]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([op,0,2,0,p4,p5])+bytes(250));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x20000880,bytes([status]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];writes=[];stop=[False]
  def hook(uc,a,size,_):
   if a in [0x0800680c,sym['case_binary_local_send']&~1]:
    p=uc.reg_read(UC_ARM_REG_R0);count=uc.reg_read(UC_ARM_REG_R1);ev.append(['send',count,bytes(uc.mem_read(p,count)).hex()]);stop[0]=True;uc.emu_stop()
   elif a in [0x080068d0,sym['case_binary_local_ack']&~1]:
    ev.append(['ack',uc.reg_read(UC_ARM_REG_R0)]);stop[0]=True;uc.emu_stop()
   elif a in [0x08006b80,sym['case_binary_local_control_a']&~1,0x08006b98,sym['case_binary_local_control_b']&~1]:
    side='a' if a in [0x08006b80,sym['case_binary_local_control_a']&~1] else 'b';ev.append(['control',side,uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,0x1234);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a==0x08009170:raise AssertionError('unexpected stock logger')
  def wr(uc,access,a,count,v,_):
   if a==0x200000bf:writes.append([a,count,v])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start((0x08000e1c if original else sym['case_binary_linked_entry'])|1,0x20001000,count=10000)
  assert stop[0] or u.reg_read(UC_ARM_REG_PC)==0x20001000,(op,n,p4,p5,flag,original,ev)
  pair.append([ev,writes,bytes(u.mem_read(0x200000bf,1)).hex(),None if stop[0] else u.reg_read(UC_ARM_REG_R0)])
 assert pair[0]==pair[1],(op,n,p4,p5,status,flag,pair)
 rows.append([op,n,p4,p5,status,flag,pair[0]])
out=dict(status='PASS_BINARY_LINKED_LOCAL_FOUR',cases=len(rows),image_sha256=sha,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Destination byte 2; four opcodes; allocated 256-byte input.','Send and ack stop; control wrapper is controlled; no transport or GPIO effect.','Isolated branch source, not full public case_binary_command.'],rows=rows)
(D/'binary-linked-local-four-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
