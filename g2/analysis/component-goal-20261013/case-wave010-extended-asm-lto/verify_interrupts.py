#!/usr/bin/env python3
"""Real native/source critical state and invalid nesting loops, no stubs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
import hashlib,json,itertools,struct
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;elf=H/'interrupt-entries.elf';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
entries={'case_kernel_enter':0x0800bffc,'case_kernel_exit':0x0800c014,'case_kernel_mode':0x0800ca4c,'case_policy_scheduler_lock':0x0800bffc,'case_policy_scheduler_unlock':0x0800c014,'case_policy_task_reschedule':0x0800c0a0,'case_policy_task_sleep_enter':0x0800c380};rows=[]
for name,depth,mask,active,suspend in itertools.product(entries,[0,1,2,3,0xffffffff],[0,1],[0,1],[0,1]):
 pair=[];fault=name in ['case_kernel_exit','case_policy_scheduler_unlock'] and depth==0
 for native in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
  if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
  else:
   for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x1000)
  for a,v in [(0x2000019c,depth),(0x20000158,suspend),(0x2000013c,active)]:u.mem_write(a,struct.pack('<I',v))
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_R0,0x12345678)
  address=entries[name] if native else sym[name];u.emu_start(address|1,0x20001000,count=500);pc=u.reg_read(UC_ARM_REG_PC)
  if fault:
   assert pc!=0x20001000 and u.reg_read(UC_ARM_REG_PRIMASK)==1;u.emu_start(pc|1,0,count=100);assert u.reg_read(UC_ARM_REG_PC)==pc
  else:assert pc==0x20001000 and u.reg_read(UC_ARM_REG_SP)==0x20008000
  value=u.reg_read(UC_ARM_REG_R0) if name in ['case_kernel_mode','case_policy_scheduler_unlock','case_policy_task_reschedule'] and not fault else None
  pair.append((bytes(u.mem_read(0x20000100,256)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),value))
 assert pair[0]==pair[1],(name,depth,mask,active,suspend,pair);rows.append({'symbol':name,'native_entry':hex(entries[name]),'depth':depth,'initial_PRIMASK':mask,'active':active,'suspend':suspend,'invalid_nesting_loop':fault,'final_PRIMASK':pair[0][2],'return_value':pair[0][3]})
r={'status':'PASS_REAL_NATIVE_C_INTERRUPT_STATE','cases':len(rows),'invalid_nesting_cases':sum(x['invalid_nesting_loop'] for x in rows),'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'limits':['Actual native/source bodies, barriers and source-derived native invalid-state loops execute; no opcode fixture/trap substitute or child stubs.','PRIMASK, RAM, SCB, defined return values and valid-return SP compared. Physical interrupt timing/scheduler arbitration not validated.','Additional roots retain real module entries only; production39rootprofile qualified separately.']};(H/'interrupt-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['invalid_nesting_cases'])
