#!/usr/bin/env python3
"""CASE b024 stock/C timer list insert decision oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_timer_due_candidate.c';obj=H/'timer_insert.oracle.o';stub=H/'timer_insert.oracle_stub.c';stubobj=H/'timer_insert.oracle_stub.o';elf=H/'timer_insert.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_task_list_insert_sorted(uint32_t a,uint32_t b){(void)a;(void)b;}\nvoid case_policy_task_unlink(uint32_t a){(void)a;}\nuint32_t case_policy_task_event_send(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 1;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xb024)
for i in range(192):
 next=rng.getrandbits(8);now=rng.getrandbits(8);previous=rng.getrandbits(8);period=rng.getrandbits(8);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000170,struct.pack('<2I',0x20004100,0x20004200));u.mem_write(0x20002018,struct.pack('<I',period))
  u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_R1,next);u.reg_write(UC_ARM_REG_R2,now);u.reg_write(UC_ARM_REG_R3,previous);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  target=0x0800bfb0 if native else sym['case_policy_task_list_insert_sorted']&~1;calls=[]
  def hook(uc,a,size,_):
   if a!=target:return
   calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b024 if native else sym['case_boot_timer_insert'])|1,0x20008000,count=130)
  pair.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20002000,0x20))))
 assert pair[0]==pair[1],(i,next,now,previous,period,pair[0][:2],pair[1][:2])
print('PASS_CASE_TIMER_INSERT',192)
