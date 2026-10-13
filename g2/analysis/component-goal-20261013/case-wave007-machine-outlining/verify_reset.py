#!/usr/bin/env python3
"""Native/source reset chain to genuine application entry; no modeled CRT."""
from pathlib import Path
import hashlib,json,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_CPU_ARM_CORTEX_M0
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';elf=HERE/'selective/case.elf';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[]
for seed in [0,0xa5,255]:
 pair=[]
 for native in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
  if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
  else:
   for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes([seed])*0x10000);u.reg_write(UC_ARM_REG_SP,0x20002c88);u.reg_write(UC_ARM_REG_LR,0x20008001)
  cut=0x0800a598 if native else sym['case_application_entry_a598']&~1;visited=[]
  def hook(uc,a,size,data):
   if a==cut:visited.append(a);uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x08000145,0x20008000,count=500000);assert visited,(native,seed,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append({'SP':u.reg_read(UC_ARM_REG_SP),'RAM':bytes(u.mem_read(0x20000000,0x2c88))})
 a,b=pair;diff=[i for i,(x,y) in enumerate(zip(a['RAM'],b['RAM'])) if x!=y]
 row={'seed':seed,'native_SP':hex(a['SP']),'source_SP':hex(b['SP']),'RAM_difference_offsets':diff,'prefix_420_equal':a['RAM'][:420]==b['RAM'][:420],'native_RAM_sha256':hashlib.sha256(a['RAM']).hexdigest(),'source_RAM_sha256':hashlib.sha256(b['RAM']).hexdigest(),'BSS_before_stack_equal':a['RAM'][420:0x2c60]==b['RAM'][420:0x2c60]}
 rows.append(row)
assert all(x['RAM_difference_offsets']==[] and x['native_SP']==x['source_SP']=='0x20002c88' for x in rows)
r={'status':'PASS_NATIVE_SOURCE_RESET_CHAIN','firmware_sha256':sha(fw),'ELF_sha256':sha(elf),'cases':rows,'limits':['Real native/source reset, early hook, CRT, zeroing and application veneer execute until genuine application entry.','Stops before application entry first instruction; stack words/register liveness at application consumers still require separate qualification.','No hardware, flash or byte-identical build acceptance.']};(HERE/'reset-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
