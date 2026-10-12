#!/usr/bin/env python3
"""Authenticated stock/source destination-not-2 0x3d routing comparison."""
from pathlib import Path
import hashlib,itertools,json,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
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
frames=[(5,0,0,0,0),(6,0,0,0,0),(4,0,0,0,0),(5,1,0,0,0),(5,0,2,0,0),(6,0,0,1,0),(7,0,0,1,0),(7,0,0,0,1)]
rows=[]
for dest,mode,active,flag,(length,b1,b2,b3,b4) in itertools.product([0,1,3],[0,1],[0,1],[0,1],frames):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([0x3d,b1,dest,b3,b4])+bytes(251));
  u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x200000f0,struct.pack('<I',0x20005000));u.mem_write(0x200000f5,bytes([active]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,mode);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];stop=[False]
  def hook(uc,a,size,_):
   if a in [0x0800a888,sym['case_binary_3d_control']&~1]:
    ev.append(['control',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);uc.reg_write(UC_ARM_REG_R0,0x9876);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08009170,sym['case_binary_3d_logger']&~1]:
    ev.append(['log',z(uc,uc.reg_read(UC_ARM_REG_R0))]);uc.reg_write(UC_ARM_REG_R0,0x1234);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x080001b4,sym['case_binary_3d_dispatch']&~1]:
    ev.append(['dispatch',uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),5)).hex(),uc.reg_read(UC_ARM_REG_R2)]);stop[0]=True;uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000e1c if original else sym['case_binary_command_candidate'])|1,0x20001000,count=10000)
  assert stop[0] or u.reg_read(UC_ARM_REG_PC)==0x20001000,(dest,mode,active,flag,length,original,ev)
  pair.append([ev,bytes(u.mem_read(0x200000bf,1)).hex(),None if stop[0] else u.reg_read(UC_ARM_REG_R0)])
 assert pair[0]==pair[1],(dest,mode,active,flag,length,b1,b2,b3,b4,pair)
 rows.append([dest,mode,active,flag,length,b1,b2,b3,b4,pair[0]])
out=dict(status='PASS_BINARY_3D_BOUNDED',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_3d_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Only destination bytes 0,1,3; opcode 3d; allocated 256-byte frame.','Control/logger controlled, stop at dispatch child; no lower or transport effects.','Isolated branch, not full case_binary_command.'],rows=rows)
(D/'binary-whole-3d-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
