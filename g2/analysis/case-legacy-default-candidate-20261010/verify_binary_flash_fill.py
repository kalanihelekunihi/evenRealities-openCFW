#!/usr/bin/env python3
"""Authenticated stock/source flash-copy wrappers with synthetic external flash data."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_flash_fill.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for kind,offset,variant in itertools.product(['51','5f'],[0,1,4],[0,1,2,3]):
 size=8 if kind=='51' else 16;address=0x0803f800 if kind=='51' else 0x0803f000
 data=[bytes(size),bytes(range(size)),bytes([0xff])*size,bytes((i*17+3)&255 for i in range(size))][variant]
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,raw);u.mem_write(address,data);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  dest=0x20004000+offset;u.mem_write(0x20004000,bytes([0xa5])*32);u.reg_write(UC_ARM_REG_R0,dest);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  entry=(0x08002f60 if kind=='51' else 0x08002f88) if original else sym['case_binary_fill'+kind]
  u.emu_start(entry|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000,(kind,offset,variant,original)
  pair.append([u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20004000,32)).hex()])
 assert pair[0]==pair[1],(kind,offset,variant,pair)
 rows.append([kind,offset,variant,data.hex(),pair[0]])
out=dict(status='PASS_BINARY_FLASH_FILL_WRAPPERS',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_flash_fill_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Synthetic bytes supplied at stock flash addresses 0x0803f800 and 0x0803f000, outside the pinned image.','Proves copy algorithm and destination-pointer R0 in emulator; does not establish actual device flash contents or physical bus behavior.','Source routines are not selected into public CASE archive.'],rows=rows)
(D/'binary-flash-fill-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
