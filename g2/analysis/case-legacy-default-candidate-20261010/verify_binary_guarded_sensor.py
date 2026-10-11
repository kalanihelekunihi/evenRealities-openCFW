#!/usr/bin/env python3
"""Stock/source 0x080035b8 recursion-guarded sensor wrapper."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_guarded_sensor.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for selector,length,guard,ret,value in itertools.product([0,6,0xab,0xffffffff],[0,1,2],[0,1,0x7f],[0,1,0xffffffff],[0,0xff]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20000029,bytes([guard]));u.mem_write(0x20004000,b'\x5a\x5b');u.reg_write(UC_ARM_REG_R0,selector);u.reg_write(UC_ARM_REG_R1,0x20004000);u.reg_write(UC_ARM_REG_R2,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,a,size,_):
   if a in [0x080028b4,0x0010f000]:
    calls.append([uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),bytes(uc.mem_read(0x20000029,1)).hex()]);uc.mem_write(0x20004000,bytes([value]));uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x080035b8 if original else sym['case_binary_guarded_sensor_read'])|1,0x20001000,count=1000)
  row=[calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000029,1)).hex(),bytes(u.mem_read(0x20004000,2)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(selector,length,guard,ret,value,pair)
 rows.append([selector,length,guard,ret,value,pair[0]])
out=dict(status='PASS_BINARY_GUARDED_SENSOR',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_guarded_sensor_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Sensor transaction 0x080028b4 controlled; physical bus effects remain unowned.','Full integer selector/length corpus bounded to listed vectors.','No public binary handler admission.'],rows=rows)
(D/'binary-guarded-sensor-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
