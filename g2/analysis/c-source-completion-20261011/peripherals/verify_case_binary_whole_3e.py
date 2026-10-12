#!/usr/bin/env python3
"""Authenticated stock/source destination-2 0x3e branch to ack boundary."""
from pathlib import Path
import hashlib,itertools,json,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[3];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'case-binary-whole.elf'
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
for length,old,incoming,active,flag,mutate in itertools.product([0,4,5,20],[0,1,2],[0,1,2],[0,1],[0,1],[0,1]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([0x3e,0,2,0,incoming])+bytes(251));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x200000f0,struct.pack('<I',0x20005000));u.mem_write(0x200000f4,bytes([old,active,0,0])+struct.pack('<I',0x12345678));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];writes=[];stopped=[False]
  def hook(uc,a,size,_):
   if a in [0x0800a888,sym['case_binary_3e_control']&~1]:
    ev.append(['control',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);
    if mutate:uc.mem_write(0x200000bf,b'\x01')
    uc.reg_write(UC_ARM_REG_R0,0x98765432);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08009170,sym['case_binary_3e_logger']&~1]:
    ev.append(['log',z(uc,uc.reg_read(UC_ARM_REG_R0))]);uc.reg_write(UC_ARM_REG_R0,0x55aa);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x080068d0,sym['case_binary_3e_ack']&~1]:
    ev.append(['ack',uc.reg_read(UC_ARM_REG_R0)]);stopped[0]=True;uc.emu_stop()
  def wr(uc,access,a,n,v,_):
   if a in [0x200000f4,0x200000fc]:writes.append([a,n,v])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start((0x08000e1c if original else sym['case_binary_command_candidate'])|1,0x20001000,count=10000)
  assert stopped[0] or u.reg_read(UC_ARM_REG_PC)==0x20001000,(length,old,incoming,active,flag,original,ev)
  pair.append([ev,writes,bytes(u.mem_read(0x200000bf,1)).hex(),bytes(u.mem_read(0x200000f4,12)).hex(),None if stopped[0] else u.reg_read(UC_ARM_REG_R0)])
 assert pair[0]==pair[1],(length,old,incoming,active,flag,mutate,pair)
 rows.append([length,old,incoming,active,flag,mutate,pair[0]])
out=dict(status='PASS_BINARY_3E_BOUNDED',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_3e_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Destination byte 2; opcode 3e; allocated 256-byte input even for short logical length.','Control, logger and ack controlled lower boundaries; no physical aging action or send claim.','Isolated branch, not full case_binary_command.'],rows=rows)
(D/'binary-whole-3e-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
