#!/usr/bin/env python3
"""Stock/source sensor start sequence 0x0800a4b4 at GPIO/delay cuts."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_sensor_start.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for initial,seed in itertools.product([0,1,0xffffffff,0x12345678],[0,1,0xdeadbeef]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.reg_write(UC_ARM_REG_R0,initial);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,a,size,_):
   group={0x0800a550:'a',0x0010f000:'a',0x0800a574:'b',0x0010f100:'b',0x0800a408:'delay',0x0010f200:'delay'}.get(a)
   if group:
    calls.append([group,None if group=='delay' else uc.reg_read(UC_ARM_REG_R0)])
    uc.reg_write(UC_ARM_REG_R0,(seed+len(calls))&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x0800a4b4 if original else sym['case_binary_sensor_start'])|1,0x20001000,count=1000)
  row=[calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(initial,seed,pair)
 assert pair[0][0]==[['a',1],['b',1],['delay',None],['b',0],['delay',None],['a',0],['delay',None]],pair
 rows.append([initial,seed,pair[0]])
out=dict(status='PASS_BINARY_SENSOR_START_SEQUENCE',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_sensor_start_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Line helpers and delay controlled; physical GPIO waveform/timing unverified.','Isolated subbranch; transaction 0x080028b4 remains unowned and no linked public provider selected.'],rows=rows)
(D/'binary-sensor-start-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
