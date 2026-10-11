#!/usr/bin/env python3
"""Bounded original/source comparisons for 0x0160, 0x2edc, 0xa7b0, 0xaa00."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_sensor_lowers_candidate.c';obj=H/'application_policy_sensor_lowers.oracle.o';stub=H/'application_policy_sensor_lowers.oracle_stub.c';stub_obj=H/'application_policy_sensor_lowers.oracle_stub.o';elf=H/'application_policy_sensor_lowers.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('''#include <stdint.h>\nvoid case_policy_adc_open(uint32_t x){(void)x;}\nvoid case_policy_adc_settle(uint32_t x,uint32_t y){(void)x;(void)y;}\nuint32_t case_policy_adc_read(uint32_t x){(void)x;return 0;}\nvoid case_policy_adc_close(uint32_t x){(void)x;}\nvoid case_policy_task_sleep(uint32_t x){(void)x;}\nvoid case_policy_task_cancel_core(uint32_t x){(void)x;}\n''')
subprocess.run(flags+[str(stub),'-o',str(stub_obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stub_obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x2edc)
def run(native,entry,args=(0,0),external=None,readings=None):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
 u.mem_map(0x00100000,0x10000)
 for a,b in seg:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
 u.reg_write(UC_ARM_REG_R0,args[0]);u.reg_write(UC_ARM_REG_R1,args[1]);trace=[]
 def hook(uc,addr,size,_):
  kind=(external or {}).get(addr)
  if kind is None:return
  trace.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if kind=='settle' else (kind,uc.reg_read(UC_ARM_REG_R0)))
  if kind=='read':uc.reg_write(UC_ARM_REG_R0,readings[sum(v[0]=='read' for v in trace)-1])
  uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((entry if native else sym[entry])|1,0x20001000,count=5000)
 return u.reg_read(UC_ARM_REG_R0),trace

for i in range(128):
 a=rng.randrange(2**32);b=([0,1,2,3,6,1000,0xffffffff][i%7] if i<70 else rng.randrange(2**32))
 n=run(True,0x08000160,(a,b))[0];c=run(False,'case_policy_sensor_divide',(a,b))[0]
 assert n==c,(i,a,b,n,c)
print('PASS_CASE_POLICY_SENSOR_DIVIDE',128)

for i in range(80):
 readings=[rng.randrange(0x10000) for _ in range(8)]
 pairs=[]
 for native in (True,False):
  ext=({0x080047d4:'open',0x08004710:'settle',0x08004328:'read',0x0800483c:'close'} if native else {sym['case_policy_adc_open']&~1:'open',sym['case_policy_adc_settle']&~1:'settle',sym['case_policy_adc_read']&~1:'read',sym['case_policy_adc_close']&~1:'close'})
  pairs.append(run(native,0x08002edc if native else 'case_policy_sensor_sample',external=ext,readings=readings))
 assert pairs[0]==pairs[1],(i,pairs)
print('PASS_CASE_POLICY_SENSOR_SAMPLE',80)

for name,addr,child,child_addr in [('case_policy_sensor_delay',0x0800a7b0,'case_policy_task_sleep',0x0800c128),('case_policy_task_cancel',0x0800aa00,'case_policy_task_cancel_core',0x0800c228)]:
 for i in range(64):
  arg=[0,1,3,0x20000100][i%4]
  p=[]
  for native in (True,False):
   ext={child_addr:'child'} if native else {sym[child]&~1:'child'}
   p.append(run(native,addr if native else name,(arg,0),external=ext))
  assert p[0]==p[1],(name,i,p)
 print('PASS_CASE_POLICY_'+('SENSOR_DELAY' if name.endswith('delay') else 'TASK_CANCEL'),64)
