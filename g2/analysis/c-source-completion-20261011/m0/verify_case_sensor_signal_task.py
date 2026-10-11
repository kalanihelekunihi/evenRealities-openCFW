#!/usr/bin/env python3
"""Bounded CASE 0xc4de task notification original/C comparison, empty waiter list."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_finish_signal_task_candidate.c'
obj=H/'sensor_signal_task.oracle.o';stub=H/'sensor_signal_task.oracle_stub.c';stubobj=H/'sensor_signal_task.oracle_stub.o';elf=H/'sensor_signal_task.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_task_sleep_enter(void){}\nvoid case_unblock_waiter(void *a,uint32_t b){(void)a;(void)b;}\nuint32_t case_policy_task_sleep_exit(void){return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc4de)
for i in range(192):
 initial=rng.randrange(0x1000000);bits=rng.randrange(0x1000000);pair=[]
 option=(rng.randrange(0x1000000)|1)|(0x04000000 if i%4==0 else 0)|(0x01000000 if i%3==0 else 0)
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x20003000,struct.pack('<I',initial));u.mem_write(0x20003010,struct.pack('<I',0x20003100 if i%2 else 0x2000300c))
  u.mem_write(0x20003100,struct.pack('<II',option,0x2000300c))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,bits)
  targets=({0x0800c380:'enter',0x0800c1cc:'unblock',0x0800cc0c:'exit'} if native else {sym['case_policy_task_sleep_enter']&~1:'enter',sym['case_unblock_waiter']&~1:'unblock',sym['case_policy_task_sleep_exit']&~1:'exit'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append(kind)
   if kind=='unblock':calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800c4de if native else sym['case_boot_sensor_finish_signal_task'])|1,0x20008000,count=500)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,0x20)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SENSOR_SIGNAL_TASK',192)
