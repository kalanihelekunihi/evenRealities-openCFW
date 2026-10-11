#!/usr/bin/env python3
"""CASE 0x2cc0 native/source OTA checksum at log cut."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_box_apply_file_candidate.c';obj=H/'apply_file.oracle.o';stub=H/'apply_file.oracle_stub.c';stubobj=H/'apply_file.oracle_stub.o';elf=H/'apply_file.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_log(uint32_t a,...){return a;}\n');subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x2cc0)
for i in range(160):
 size=i%41;sample=rng.randbytes(44);total=sum(int.from_bytes(sample[j:j+4],'big') for j in range(0,size,4))&0xffffffff;expected=total if i%3==0 else rng.getrandbits(32);quiet=i%2;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x08040000,0x1000);u.mem_write(0x08040000,sample);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000089c,struct.pack('<II',size,expected));u.mem_write(0x200000bf,bytes([quiet]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  target=0x08009170 if native else sym['case_policy_log']&~1;calls=[]
  def hook(uc,a,n,_):
   if a==target:
    x=uc.reg_read(UC_ARM_REG_R0);calls.append((bytes(uc.mem_read(x,90)).split(b'\0')[0],uc.reg_read(UC_ARM_REG_R1) if len(calls)==0 else None,uc.reg_read(UC_ARM_REG_R2) if len(calls)==0 else None));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08002cc0 if native else sym['case_policy_box_apply_file'])|1,0x20008000,count=1000)
  pair.append((u.reg_read(UC_ARM_REG_R0),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOX_APPLY_FILE',160)
