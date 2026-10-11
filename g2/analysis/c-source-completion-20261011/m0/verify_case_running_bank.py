#!/usr/bin/env python3
"""CASE 0x2f46 running bank native/source option-word cut."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_box_running_bank_candidate.c';obj=H/'bank.oracle.o';stub=H/'bank.oracle_stub.c';stubobj=H/'bank.oracle_stub.o';elf=H/'bank.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_read_option_words(uint32_t *words){(void)words;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x2f46)
for i in range(128):
 words=[rng.getrandbits(32) for _ in range(7)];words[6]=(words[6]&~0x100000)|((i&1)<<20);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  target=0x08004a00 if native else sym['case_boot_read_option_words']&~1;calls=[]
  def hook(uc,a,n,_):
   if a==target:
    x=uc.reg_read(UC_ARM_REG_R0);calls.append(x);uc.mem_write(x,struct.pack('<7I',*words));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08002f46 if native else sym['case_policy_box_running_bank'])|1,0x20008000,count=100)
  pair.append((u.reg_read(UC_ARM_REG_R0),len(calls)))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_RUNNING_BANK',128)
