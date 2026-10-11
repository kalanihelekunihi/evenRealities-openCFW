#!/usr/bin/env python3
"""Stock/source 0x0800a130 counted-read adapter at guarded sensor cut."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_sensor_counted_adapter.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for selector,length,value,lower_result in itertools.product([0,2,14,0xffffffff],[0,1,2,255],[0,0x7f,0xff],[0,1,0xffffffff]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,b'\x5a');u.reg_write(UC_ARM_REG_R0,selector);u.reg_write(UC_ARM_REG_R1,0x20004000);u.reg_write(UC_ARM_REG_R2,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,a,size,_):
   if a in [0x080035b8,0x0010f000]:
    p=uc.reg_read(UC_ARM_REG_R1);calls.append([uc.reg_read(UC_ARM_REG_R0),p,uc.reg_read(UC_ARM_REG_R2),bytes(uc.mem_read(p,1)).hex()]);uc.mem_write(p,bytes([value]));uc.reg_write(UC_ARM_REG_R0,lower_result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x0800a130 if original else sym['case_binary_sensor_read_adapter'])|1,0x20001000,count=1000)
  row=[calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20004000,1)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(selector,length,value,lower_result,pair)
 rows.append([selector,length,value,lower_result,pair[0]])
out=dict(status='PASS_BINARY_SENSOR_COUNTED_ADAPTER',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_sensor_read_lower_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Guarded sensor lower 0x080035b8 controlled; its child 0x080028b4 and hardware effects remain unowned.','Length forwarded unchanged; physical sensor protocol unproved.','No public binary handler admission.'],rows=rows)
(D/'binary-sensor-counted-adapter-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
