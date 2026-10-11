#!/usr/bin/env python3
"""CASE 0x0102 PendSV original/C architectural register and stack oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_pendsv_vector_candidate.c';obj=H/'pendsv_vector.oracle.o';stub=H/'pendsv_vector.oracle_stub.c';stubobj=H/'pendsv_vector.oracle_stub.o';elf=H/'pendsv_vector.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('void case_policy_task_wake_dispatch(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x0102)
for i in range(96):
 old=[rng.getrandbits(32) for _ in range(8)];new=[rng.getrandbits(32) for _ in range(8)];pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000128,struct.pack('<I',0x20003000));u.mem_write(0x20003100,struct.pack('<I',0x20006000));u.mem_write(0x20006000,struct.pack('<8I',*new))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_PSP,0x20007020);u.reg_write(UC_ARM_REG_LR,0x20008001)
  for reg,v in zip([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11],old):u.reg_write(reg,v)
  target=0x0800c390 if native else sym['case_policy_task_wake_dispatch']&~1
  calls=[]
  def hook(uc,a,size,_):
   if a!=target:return
   calls.append(a);uc.mem_write(0x20000128,struct.pack('<I',0x20003100));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08000102 if native else sym['case_vector_pendsv_0102'])|1,0x20008000,count=300)
  pair.append((bytes(u.mem_read(0x20006ff0,0x30)),u.reg_read(UC_ARM_REG_PSP),u.reg_read(UC_ARM_REG_PRIMASK),[u.reg_read(x) for x in [UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]],len(calls)))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_PENDSV_VECTOR',96)
