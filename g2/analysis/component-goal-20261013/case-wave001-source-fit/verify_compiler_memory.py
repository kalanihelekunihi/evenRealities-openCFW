#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;elf=HERE/'case.elf'
with elf.open('rb') as f:
 e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[];sizes=[0,1,2,3,4,7,8,9,31,32,33,127,128,255,256,511,512]
for kind,size,source_offset,dest_offset in itertools.product(['memcpy','memset'],sizes,[0,1,3],[0,1,3]):
 for fill in ([0] if kind=='memcpy' else [0,0x7f,0xff,0x1234]):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);source=bytes((i*73+11)&255 for i in range(1024));destination=bytearray([0xa5]*1024);u.mem_write(0x20002000,source);u.mem_write(0x20005000,bytes(destination));target=0x20005000+dest_offset;value=0x20002000+source_offset if kind=='memcpy' else fill
  for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[target,value,size]):u.reg_write(reg,v)
  u.reg_write(UC_ARM_REG_SP,0x2000e000);u.reg_write(UC_ARM_REG_LR,0x2000f001);u.emu_start(symbols[kind]|1,0x2000f000,count=30000)
  assert u.reg_read(UC_ARM_REG_PC)==0x2000f000 and u.reg_read(UC_ARM_REG_SP)==0x2000e000 and u.reg_read(UC_ARM_REG_R0)==target
  destination[dest_offset:dest_offset+size]=source[source_offset:source_offset+size] if kind=='memcpy' else bytes([fill&255])*size
  assert bytes(u.mem_read(0x20005000,1024))==bytes(destination)
  assert bytes(u.mem_read(0x20002000,1024))==source
  rows.append({'operation':kind,'size':size,'source_offset':source_offset,'dest_offset':dest_offset,'fill':fill})
r={'status':'PASS_AUTHORED_GNU_PROFILE_MEMORY_PROVIDERS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((HERE/'compiler_memory.c').read_bytes()).hexdigest(),'limits':['Standard nonoverlapping valid-buffer copy/fill domain only; no native-function/body coverage attribution.','No hardware, zero-length null-pointer, overlap or pointer-overflow guarantee.']};(HERE/'compiler-memory-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
