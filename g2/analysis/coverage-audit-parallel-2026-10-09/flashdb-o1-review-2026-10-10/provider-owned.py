from pathlib import Path
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
import struct,json
D=Path('/repo/g2/analysis/flashdb-o1-read-diagnosis-20261010-implementation')
with (D/'provider-owned.elf').open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for requested in [3,8,12]:
 for hook in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x100000);u.mem_map(0x800000,0x1000)
  for a,b in sections:u.mem_write(a,b)
  sp=0x200ff000;u.mem_write(sp,struct.pack('<I',0x20040000));u.mem_write(0x20020000,b'key\0')
  for r,v in [(UC_ARM_REG_R0,0x20010000),(UC_ARM_REG_R1,0x20020000),(UC_ARM_REG_R2,0x20030000),(UC_ARM_REG_R3,requested),(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,0x800001)]:u.reg_write(r,v)
  if hook:u.hook_add(UC_HOOK_MEM_WRITE,lambda u,acc,a,n,v,d:None)
  u.emu_start(syms['test_get']|1,0x800000,count=10000);assert u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x800000
  address=int.from_bytes(u.mem_read(syms['read_address'],4),'little');count=int.from_bytes(u.mem_read(syms['read_count'],4),'little');ret=u.reg_read(UC_ARM_REG_R0);assert ret==min(requested,8) and count==ret
  if not hook:assert address==0xabc400
  rows.append({'requested':requested,'valid_memory_write_hook':hook,'read_address':hex(address),'read_count':count,'return':ret,'value_len':int.from_bytes(u.mem_read(0x20040000,4),'little'),'matches_expected_address':address==0xabc400,'provider_redirection_hooks':False})
Path('/tmp/flashdb-o1-audit-provider-owned-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
