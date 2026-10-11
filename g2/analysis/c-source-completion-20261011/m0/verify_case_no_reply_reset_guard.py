#!/usr/bin/env python3
"""Bounded stock/C oracle for 0x9a9c return, guarded-busy and quiet paths."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_no_reply_reset_candidate.c'
obj=H/'no_reply_reset_guard.oracle.o';stub=H/'no_reply_reset_guard.oracle_stub.c';stubobj=H/'no_reply_reset_guard.oracle_stub.o';elf=H/'no_reply_reset_guard.oracle.elf'
data_src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_registration_data_candidate.c';dataobj=H/'no_reply_reset_guard.data.o'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
subprocess.run(flags+[str(data_src),'-o',str(dataobj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_log(uint32_t x){return x;}\nvoid case_policy_sensor_prepare(void){}\nuint32_t case_policy_sensor_shutdown(uint32_t x){return x;}\nvoid case_bus_gpio_config(uint32_t x,volatile uint32_t*y){(void)x;(void)y;}\nvoid case_policy_ota_left_prepare(void){}\nvoid case_policy_ota_right_prepare(void){}\nvoid case_policy_reset_pulse(void){}\nvoid case_policy_ota_left_finish(void){}\nvoid case_policy_ota_right_finish(void){}\nint32_t case_policy_sensor_delay(uint32_t x){return (int32_t)x;}\nvoid case_policy_idle_clear(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(dataobj),str(stubobj),'-o',str(elf)],check=True)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x9a9c)
for i in range(192):
 left=rng.randrange(4);right=rng.randrange(4);guard=i%3!=0;quiet=i%4==0
 if i%5==0:left=right=0
 if not guard and (left|right):guard=True
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000bc,bytes([int(guard),0,0,int(quiet)]))
  u.reg_write(UC_ARM_REG_R0,left);u.reg_write(UC_ARM_REG_R1,right);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  log=0x08009170 if native else sym['case_policy_log']&~1;calls=[]
  def hook(uc,a,size,_):
   if a!=log:return
   calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08009a9c if native else sym['case_policy_no_reply_reset'])|1,0x20008000,count=1000)
  pair.append((calls,bytes(u.mem_read(0x200000bc,4))))
 assert pair[0]==pair[1],(i,left,right,guard,quiet,pair)
print('PASS_CASE_NO_REPLY_RESET_GUARD',192)
