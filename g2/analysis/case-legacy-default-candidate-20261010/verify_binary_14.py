#!/usr/bin/env python3
"""Authenticated stock/source opcode 0x14 through controlled children/send."""
from pathlib import Path
import hashlib,itertools,json,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_14.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[];vectors=[(0,0,0,0),(0x1234,0x4321,0x9876,0x55),(0xffffffff,0x80000000,0xabcdef12,0xfe),(0x76543210,0xffffffff,0x10001,0x80)]
for length,flag,(a,b,c,byte),scaled in itertools.product([0,1,5,20],[0,1],vectors,[0,0x80000001,0x1234]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for addr,data in segments:u.mem_write(addr,data)
  u.mem_write(0x20004000,bytes([0x14,0,2])+bytes(253));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087d,bytes([byte]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];stopped=[False]
  def hook(uc,pc,size,_):
   if pc in [0x08009ff0,0x0010f000,0x08009f18,0x0010f200,0x0800a01e,0x0010f300]:
    p=uc.reg_read(UC_ARM_REG_R0);name='a' if pc in [0x08009ff0,0x0010f000] else 'b' if pc in [0x08009f18,0x0010f200] else 'c';ev.append([name,bytes(uc.mem_read(p,4)).hex()]);uc.mem_write(p,struct.pack('<I',{'a':a,'b':b,'c':c}[name]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif pc in [0x0800018c,0x0010f100]:
    ev.append(['scale',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);uc.reg_write(UC_ARM_REG_R0,scaled);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif pc in [0x0800680c,0x0010f400]:
    p=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);ev.append(['send',n,bytes(uc.mem_read(p,n)).hex()]);stopped[0]=True;uc.emu_stop()
   elif pc==0x08009170:raise AssertionError('unexpected logger')
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000e1c if original else sym['case_binary_14_candidate'])|1,0x20001000,count=10000)
  assert stopped[0],(length,flag,original,ev)
  pair.append([ev,bytes(u.mem_read(0x200000bf,1)).hex()])
 assert pair[0]==pair[1],(length,flag,a,b,c,byte,scaled,pair)
 rows.append([length,flag,a,b,c,byte,scaled,pair[0]])
out=dict(status='PASS_BINARY_14_BOUNDED',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_14_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Destination byte 2; opcode 0x14; allocated 256-byte command input.','Four value children and scale return controlled; stop at send. No producer, transport or hardware claim.','Isolated branch, not full case_binary_command.'],rows=rows)
(D/'binary-14-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
