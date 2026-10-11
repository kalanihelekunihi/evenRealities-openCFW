#!/usr/bin/env python3
"""Linked stock/source binary 0x14 through source-owned A/C reader wrappers."""
from pathlib import Path
import hashlib,itertools,json,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_linked_entry.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for length,flag,abyte,cword,bmode,bsample in itertools.product([0,20],[0,1],[0,80,0xff],[0,0xffff],[0,1,64],[0,0x8000,0xffff]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x20000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([0x14,0,2])+bytes(253));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087d,b'\x57');u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];stop=[False]
  def hook(uc,a,size,_):
   if a in [0x080028b4,0x0010f360]:
    code=uc.reg_read(UC_ARM_REG_R0);p=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2);ev.append(['sensor_transaction',code,n,bytes(uc.mem_read(p,n)).hex(),bytes(uc.mem_read(0x20000029,1)).hex()]);value=(bytes([abyte]) if code==6 else bytes([bmode])) if n==1 else (cword if code==2 else bsample).to_bytes(2,'big');uc.mem_write(p,value);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x0800a148,0x0010f380]:
    ev.append(['delay',uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,0x9876);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x0800680c,sym['case_binary_14_send']&~1]:
    p=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);ev.append(['send',n,bytes(uc.mem_read(p,n)).hex()]);stop[0]=True;uc.emu_stop()
   elif a==0x08009170:raise AssertionError('unexpected logger')
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000e1c if original else sym['case_binary_linked_entry'])|1,0x20001000,count=10000)
  assert stop[0],(length,flag,abyte,cword,bmode,bsample,original,ev)
  pair.append([ev,bytes(u.mem_read(0x200000bf,1)).hex(),bytes(u.mem_read(0x20000029,1)).hex()])
 assert pair[0]==pair[1],(length,flag,abyte,cword,bmode,bsample,pair)
 rows.append([length,flag,abyte,cword,bmode,bsample,pair[0]])
out=dict(status='PASS_BINARY_LINKED_14_READERS',cases=len(rows),image_sha256=sha,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['All three reader wrappers, signed scale, byte/count adapters and guarded sensor execute; transaction and delay remain controlled.','Stops at send entry; no sensor, UART or physical behavior claim.','Test linked binary entry, not selected archive.'],rows=rows)
(D/'binary-linked-14-readers.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
