#!/usr/bin/env python3
"""CASE c83a stock/C wait-path queue receive and copy-out oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_timer_command_receive_candidate.c';obj=H/'timer_receive.oracle.o';stub=H/'timer_receive.oracle_stub.c';stubobj=H/'timer_receive.oracle_stub.o';elf=H/'timer_receive.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_scheduler_mode(void){return 1;}\nvoid case_policy_scheduler_lock(void){}\nuint32_t case_policy_scheduler_unlock(void){return 0;}\nuint32_t case_policy_task_reschedule(void){return 0;}\nuint32_t case_boot_pool_wake_waiter(uint32_t a){(void)a;return 0;}\nvoid case_policy_queue_wait_snapshot(uint32_t *a){(void)a;}\nvoid case_policy_task_sleep_enter(void){}\nuint32_t case_policy_queue_wait_elapsed(uint32_t *a,uint32_t *b){(void)a;(void)b;return 0;}\nvoid case_policy_queue_wait_cleanup(uint32_t a){(void)a;}\nuint32_t case_policy_task_sleep_exit(void){return 0;}\nvoid case_policy_queue_wait_register(uint32_t a,uint32_t b){(void)a;(void)b;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xc83a)
for i in range(96):
 q=bytearray(0x80);data=rng.randbytes(0x50);count=0;read=0x20003030 if i%4==0 else 0x20003000;waiter=i%2;wake=i%5==0;elapsed=i%2==0
 for off,val in [(0,0x20003000),(8,0x20003040),(12,read),(16,waiter),(56,count),(64,16)]:struct.pack_into('<I',q,off,val)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,bytes(q));u.mem_write(0x20003000,data)
  u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_R1,0x20004000);u.reg_write(UC_ARM_REG_R2,10);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800ca4c:'mode',0x0800bffc:'lock',0x0800c014:'unlock',0x0800cba0:'wake',0x0800c0a0:'switch',0x0800c15c:'snapshot',0x0800c380:'sleep',0x0800c948:'elapsed',0x0800b374:'cleanup',0x0800cc0c:'exit',0x0800c178:'register'} if native else {sym['case_policy_scheduler_mode']&~1:'mode',sym['case_policy_scheduler_lock']&~1:'lock',sym['case_policy_scheduler_unlock']&~1:'unlock',sym['case_boot_pool_wake_waiter']&~1:'wake',sym['case_policy_task_reschedule']&~1:'switch',sym['case_policy_queue_wait_snapshot']&~1:'snapshot',sym['case_policy_task_sleep_enter']&~1:'sleep',sym['case_policy_queue_wait_elapsed']&~1:'elapsed',sym['case_policy_queue_wait_cleanup']&~1:'cleanup',sym['case_policy_task_sleep_exit']&~1:'exit',sym['case_policy_queue_wait_register']&~1:'register'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if kind=='register' else (kind,))
   if kind=='snapshot':uc.mem_write(uc.reg_read(UC_ARM_REG_R0),bytes(8))
   if kind=='register':uc.mem_write(0x20002038,struct.pack('<I',1))
   uc.reg_write(UC_ARM_REG_R0,1 if kind=='mode' or (kind=='wake' and wake) or (kind=='elapsed' and elapsed) else 0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800c83a if native else sym['case_boot_timer_command_receive'])|1,0x20008000,count=1600)
  pair.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20002000,0x80)),bytes(u.mem_read(0x20004000,16))))
 assert pair[0]==pair[1],(i,count,hex(read),waiter,wake,pair[0][:2],pair[1][:2])
print('PASS_CASE_TIMER_COMMAND_RECEIVE_WAIT',96)
