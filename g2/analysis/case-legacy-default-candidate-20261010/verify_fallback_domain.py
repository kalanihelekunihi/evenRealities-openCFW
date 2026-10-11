#!/usr/bin/env python3
"""Source default vs fixed-image legacy entry for all non-special opcodes."""
from pathlib import Path
import hashlib,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:];elf=D/'default.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
covered=set(range(0xa0,0xb1))|{0xd0,0xd1,0xd2,0xd3,0xd4,0xdd,0xdf};special={0xee,0xff}
rows=[]
for opcode in range(256):
 if opcode in covered|special:continue
 for length in [0,1,2,4,8]:
  for flag in [0,1,0x7f]:
   pair=[]
   for original in [True,False]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
    for address,data in segments:u.mem_write(address,data)
    u.mem_write(0x20004000,bytes([opcode,0x55,0x66,0x77,0x88])+bytes(27));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087c,bytes(32));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
    lower=[];writes=[]
    def code(uc,address,size,user):
     if original and not 0x08000928<=address<0x08000c68 and not 0x08009190<=address<0x080091aa:lower.append(hex(address));uc.emu_stop()
    def write(uc,access,address,size,value,user):
     if not 0x20007fc0<=address<0x20008000:writes.append([address,size,value])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start((0x08000928 if original else sym['case_legacy_default_branch'])|1,0x20001000,count=10000)
    assert not lower,(opcode,length,flag,lower)
    pair.append(dict(return_value=u.reg_read(UC_ARM_REG_R0),state=bytes(u.mem_read(0x200000bd,4)).hex(),writes=writes))
   assert pair[0]==pair[1],(opcode,length,flag,pair)
   rows.append(dict(opcode=opcode,length=length,flag=flag,comparison=pair[0]))
out=dict(status='PASS_NON_SPECIAL_FALLBACK_DOMAIN',cases=len(rows),opcodes=256-len(covered|special),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/default.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['All 32-byte buffers allocated even at logical length zero; not physical short-frame safety.','Fixed state fields and three log flags; branch census separately confirms only ee/ff lower-boundary hits outside known dispatcher.','Does not prove lower effects or whole public legacy handler.'],rows=rows)
(D/'fallback-domain-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['opcodes'],len(rows))
