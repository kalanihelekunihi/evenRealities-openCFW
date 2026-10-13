#!/usr/bin/env python3
"""Full stock and actual two-name RAM state reset module, no children."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
import hashlib,json,random
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;elf=H/'side-state-entries.elf';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
names=['case_boot_button_mode_reset','case_policy_fake_standby_set'];assert sym[names[0]]!=sym[names[1]];rng=random.Random(0x3a00);values=[0,1,2,3,127,128,255,256,65535,0x7fffffff,0x80000000,0xffffffff]+[rng.getrandbits(32) for _ in range(128)];regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];rows=[]
for name in names:
 for value in values:
  ram=rng.randbytes(0x3000);pair=[]
  for native in [True,False]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
   if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
   else:
    for a,b in segs:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,ram);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x2000f001)
   for i,reg in enumerate(regs):u.reg_write(reg,0x13579000+i)
   u.emu_start((0x08003a00 if native else sym[name])|1,0x2000f000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x2000f000 and u.reg_read(UC_ARM_REG_SP)==0x20008000;assert [u.reg_read(r) for r in regs]==[0x13579000+i for i in range(8)];pair.append(bytes(u.mem_read(0x20000000,0x3000)))
  assert pair[0]==pair[1],(name,value);rows.append({'symbol':name,'active':value,'RAM_before_sha256':hashlib.sha256(ram).hexdigest(),'RAM_after_sha256':hashlib.sha256(pair[0]).hexdigest(),'changed_offsets':[i for i,(a,b) in enumerate(zip(ram,pair[0])) if a!=b]})
r={'status':'PASS_FULL_NATIVE_C_SIDE_STATE_MODULE','cases':len(rows),'RAM_bytes_compared_per_case':0x3000,'distinct_addresses':{n:hex(sym[n]) for n in names},'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'ABI':'Void return; SP/R4-R11 preserved; exact complete RAM state compared; no child calls/stubs/hardware model','limits':['Full native3a00 and genuine source entries execute to return; excludes concurrent IRQ/DMA writes and overall power-mode/scheduler/hardware behavior.','All-entry fixture adds real roots for module qualification; production39rootprofile separate.']};(H/'side-state-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
