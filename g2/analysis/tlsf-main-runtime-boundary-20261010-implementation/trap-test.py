from pathlib import Path
import json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).parent
with (D/'trap-comparator.elf').open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS'];symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
results=[]
for name,entry,args in [('misaligned-create','tlsf_create',[0x20080001]),('direct-assert','__assert_func',[0x20081000,1233,0x20081010,0x20081020])]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x100000)
 for a,b in sections:u.mem_write(a,b)
 u.reg_write(UC_ARM_REG_SP,0x20070000);u.reg_write(UC_ARM_REG_LR,0x110001)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 events=[]
 def interrupt(u,number,d):
  pc=u.reg_read(UC_ARM_REG_PC);assert bytes(u.mem_read(pc,2))==b'\xab\xbe' or bytes(u.mem_read(pc-2,2))==b'\xab\xbe';events.append(dict(interrupt=number,pc=hex(pc),r0=hex(u.reg_read(UC_ARM_REG_R0)),r1=u.reg_read(UC_ARM_REG_R1),r2=hex(u.reg_read(UC_ARM_REG_R2)),r3=hex(u.reg_read(UC_ARM_REG_R3))));u.emu_stop()
 u.hook_add(UC_HOOK_INTR,interrupt);u.emu_start(symbols[entry]|1,0,count=10000);assert len(events)==1;results.append(dict(name=name,entry=hex(symbols[entry]),events=events,trap_observed=True))
(D/'trap-results.json').write_text(json.dumps(dict(cases=results,elf_sha256=hashlib.sha256((D/'trap-comparator.elf').read_bytes()).hexdigest(),no_stock_diagnostic_equivalence_claim=True),indent=2)+'\n');print('Two explicit source trap-contract cases PASS')
