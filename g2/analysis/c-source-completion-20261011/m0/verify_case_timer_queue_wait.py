#!/usr/bin/env python3
"""CASE c0e0 stock/C queue wait bridge oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_timer_queue_wait_candidate.c';obj=H/'timer_queue_wait.oracle.o';stub=H/'timer_queue_wait.oracle_stub.c';stubobj=H/'timer_queue_wait.oracle_stub.o';elf=H/'timer_queue_wait.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_scheduler_lock(void){}\nuint32_t case_policy_scheduler_unlock(void){return 0;}\nvoid case_boot_timer_event_wait(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nvoid case_policy_queue_wait_cleanup(uint32_t a){(void)a;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc0e0)
for i in range(128):
 q=bytearray(rng.randbytes(0x80));q[68]=255 if i%3==0 else q[68];q[69]=255 if i%4==0 else q[69];struct.pack_into('<I',q,56,0 if i%2 else 1)
 ticks=rng.getrandbits(16);opt=rng.getrandbits(8);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,bytes(q))
  u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_R1,ticks);u.reg_write(UC_ARM_REG_R2,opt);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800bffc:'lock',0x0800c014:'unlock',0x0800c19c:'wait',0x0800b374:'release'} if native else {sym['case_policy_scheduler_lock']&~1:'lock',sym['case_policy_scheduler_unlock']&~1:'unlock',sym['case_boot_timer_event_wait']&~1:'wait',sym['case_policy_queue_wait_cleanup']&~1:'release'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
   calls.append((kind,r0,r1,r2) if kind=='wait' else (kind,r0) if kind=='release' else (kind,))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800c0e0 if native else sym['case_boot_timer_queue_wait'])|1,0x20008000,count=250)
  pair.append((calls,bytes(u.mem_read(0x20002000,0x80))))
 assert pair[0]==pair[1],(i,pair[0][0],pair[1][0])
print('PASS_CASE_TIMER_QUEUE_WAIT',128)
