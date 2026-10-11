#!/usr/bin/env python3
"""Compare stock CASE 0x02d6 CRT decoder and C body on authenticated stream."""
from pathlib import Path
import hashlib,subprocess,sys,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
compressed=F[0xd95c:0xd9c4]
with tempfile.TemporaryDirectory() as d:
 elf=Path(d)/'case.elf';subprocess.run([sys.executable,str(H/'build_case_absolute_experiment.py'),'--output',str(elf)],check=True,capture_output=True)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
  seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 outcomes=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  if native:
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  else:
   u.mem_map(0x08000000,0x20000)
   for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x300000,0x10000)
  u.mem_write(0x301000,compressed)
  u.reg_write(UC_ARM_REG_R0,0x301000);u.reg_write(UC_ARM_REG_R1,0x20000000)
  u.reg_write(UC_ARM_REG_R2,420);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x30000001)
  u.emu_start((0x080002d6 if native else sym['case_crt_decode_02d6'])|1,0x30000000,count=30000)
  outcomes.append(bytes(u.mem_read(0x20000000,420)))
 assert outcomes[0]==outcomes[1],(hashlib.sha256(outcomes[0]).hexdigest(),hashlib.sha256(outcomes[1]).hexdigest())
 assert hashlib.sha256(outcomes[0]).hexdigest()=='d91efcf9f5409364aa0e3791d1084418682e76414c5a7b588c3c484daa0dd89a'
 print('PASS_CASE_CRT_DECODE',420,hashlib.sha256(outcomes[0]).hexdigest())
