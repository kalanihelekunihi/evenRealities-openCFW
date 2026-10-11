#!/usr/bin/env python3
"""Stock/C first iteration of CASE timer-service task at b360."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_service_task_entry_candidate.c';obj=H/'timer_service_loop.oracle.o';stub=H/'timer_service_loop.oracle_stub.c';stubobj=H/'timer_service_loop.oracle_stub.o';elf=H/'timer_service_loop.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_timer_wait_next(uint32_t *d){*d=0;return 0;}\nvoid case_boot_timer_process(uint32_t a,uint32_t b){(void)a;(void)b;}\nvoid case_boot_timer_expired(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xb360)
for i in range(64):
 deadline=rng.getrandbits(32);result=rng.getrandbits(32);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_R0,i);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800ade8:'wait',0x0800b1fc:'process',0x0800b0fc:'expire'} if native else {sym['case_boot_timer_wait_next']&~1:'wait',sym['case_boot_timer_process']&~1:'process',sym['case_boot_timer_expired']&~1:'expire'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
   if kind=='wait':uc.mem_write(r0,struct.pack('<I',deadline));calls.append(('wait',));uc.reg_write(UC_ARM_REG_R0,result)
   elif kind=='process':calls.append(('process',r0,r1))
   else:calls.append(('expire',));uc.emu_stop();return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b360 if native else sym['case_boot_service_task_entry'])|1,0,count=120)
  pair.append(calls)
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_TIMER_SERVICE_LOOP',64)
