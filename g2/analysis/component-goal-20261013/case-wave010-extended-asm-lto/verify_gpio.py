#!/usr/bin/env python3
"""Full native/C GPIO MMIO leaves and real wrappers; no child cuts."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
import hashlib,json,random
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
elf=HERE/'gpio-all-entries.elf';fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
a=['case_control_a','case_binary_local_control_a','case_binary_56_clear_a','case_boot_transport_stop_clock'];b=['case_control_b','case_binary_local_control_b','case_binary_56_clear_b','case_legacy_gpio_bit4','case_boot_transport_stop_link'];assert len(set(sym[x] for x in a+b))==9
rng=random.Random(0x6b806b98);values=[0,1,2,3,127,128,255,256,65535,0x7fffffff,0x80000000,0xffffffff]+[rng.getrandbits(32) for _ in range(100)]
regs=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];rows=[]
def run(native,address,args):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
 else:
  for p,b in seg:u.mem_write(p,b)
 u.mem_map(0x20000000,0x10000);u.mem_map(0x50000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x2000f001)
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,val)
 for i,reg in enumerate(regs):u.reg_write(reg,0x13579000+i)
 writes=[]
 def hook(uc,access,p,size,value,data):
  if 0x50000000<=p<0x50010000:writes.append((hex(p),size,value))
 u.hook_add(UC_HOOK_MEM_WRITE,hook);u.emu_start(address|1,0x2000f000,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x2000f000 and u.reg_read(UC_ARM_REG_SP)==0x20008000;assert [u.reg_read(r) for r in regs]==[0x13579000+i for i in range(8)];return writes,bytes(u.mem_read(0x50000000,0x10000))
for names,original in [(a,0x08006b80),(b,0x08006b98)]:
 for name in names:
  for value in values:
   x=run(True,original,[value]);y=run(False,sym[name],[value]);assert x==y,(name,value,x[0],y[0]);rows.append({'symbol':name,'native_entry':hex(original),'enable':value,'writes':x[0]})
for base in [0x50000000,0x50000400]:
 for mask in [0,1,0x40,0x80,0xffff,0x80000000,0xffffffff]:
  for enable in values:
   args=[base,mask,enable];x=run(True,0x08004e9e,args);y=run(False,sym['case_control_write'],args);assert x==y,(args,x[0],y[0]);rows.append({'symbol':'case_control_write','native_entry':'0x08004e9e','args':args,'writes':x[0]})
r={'status':'PASS_FULL_NATIVE_C_GPIO_PROVIDER_MODULE','cases':len(rows),'comparisons':rows,'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'distinct_entry_addresses':{n:hex(sym[n]) for n in a+b},'ABI':'Void return; SP and R4-R11 preserved, exact MMIO writes and register-space memory compared. R0-R3/R12 are caller-clobbered and ignored at return.','limits':['All source and native leaf bodies execute with no child stubs/cuts. MMIO storage and writes are synthetic emulator evidence, not physical pin output proof.','Additional roots retain actual entries for module fixture only; production profile and39knownroots remain separately qualified.']};(HERE/'gpio-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
