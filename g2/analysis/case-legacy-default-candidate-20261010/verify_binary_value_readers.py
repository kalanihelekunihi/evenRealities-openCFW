#!/usr/bin/env python3
"""Authenticated stock/source 0x9ff0 and 0xa01e reader wrappers."""
from pathlib import Path
import hashlib,itertools,json,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_value_readers.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for kind,lowerret,value in itertools.product(['a','c'],[0,1,0xffffffff],[0,1,0x7f,0xff,0x12345678,0xffffffff]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,struct.pack('<I',0xdeadbeef));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];writes=[]
  def hook(uc,a,size,_):
   if a in [0x0800a124,0x0010f000,0x0800a074,0x0010f100]:
    code=uc.reg_read(UC_ARM_REG_R0);p=uc.reg_read(UC_ARM_REG_R1);ev.append(['lower',code,bytes(uc.mem_read(p,1 if kind=='a' else 4)).hex()]);uc.mem_write(p,bytes([value&0xff]) if kind=='a' else struct.pack('<I',value));uc.reg_write(UC_ARM_REG_R0,lowerret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def wr(uc,access,a,n,v,_):
   if a==0x20004000:writes.append([a,n,v])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,wr);entry=(0x08009ff0 if kind=='a' else 0x0800a01e) if original else sym['case_binary_14_read_'+kind];u.emu_start(entry|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000,(kind,original,ev)
  pair.append([ev,writes,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20004000,4)).hex()])
 assert pair[0]==pair[1],(kind,lowerret,value,pair)
 rows.append([kind,lowerret,value,pair[0]])
out=dict(status='PASS_BINARY_VALUE_READER_WRAPPERS',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_value_readers_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Only wrappers 0x08009ff0 and 0x0800a01e; lower read operations are controlled.','No sensor, PMIC or physical value provenance claim.','Provider candidates are not selected into public CASE archive.'],rows=rows)
(D/'binary-value-readers-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
