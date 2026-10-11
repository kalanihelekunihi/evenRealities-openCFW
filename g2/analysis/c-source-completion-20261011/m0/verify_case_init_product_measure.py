#!/usr/bin/env python3
"""Native/source product measurement at timer/divide child cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_init_product_measure_candidate.c';obj=H/'application_init_product_measure.oracle.o';stub=H/'application_init_product_measure.oracle_stub.c';stubobj=H/'application_init_product_measure.oracle_stub.o';elf=H/'application_init_product_measure.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nint32_t case_policy_timer_query(uint32_t a,uint32_t*b){(void)a;(void)b;return 0;}\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x9ebc)
for i in range(96):
 raw=rng.randrange(65536);failure=i%11==0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,struct.pack('<I',0xdeadbeef))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20002000)
  cuts=({0x0800a074:'query',0x08000160:'divide'} if native else {sym['case_policy_timer_query']&~1:'query',sym['case_policy_sensor_divide']&~1:'divide'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   if k=='query':
    trace.append((k,uc.reg_read(UC_ARM_REG_R0)))
    uc.mem_write(uc.reg_read(UC_ARM_REG_R1),struct.pack('<I',raw))
    uc.reg_write(UC_ARM_REG_R0,1 if failure else 0)
   else:
    x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);trace.append((k,x,y));uc.reg_write(UC_ARM_REG_R0,x//y)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08009ebc if native else sym['case_init_read_product_byte'])|1,0x20008000,count=300)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20002000,4)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_INIT_PRODUCT_MEASURE',96)
