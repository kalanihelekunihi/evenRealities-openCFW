#!/usr/bin/env python3
"""Bounded CASE native/source comparison for 0x9ebc, 9f18, 9ff0, a01e."""
from pathlib import Path
import random,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
H=Path(__file__).resolve().parent; R=H.parents[3]
firmware=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011'
files=['application_boot_battery_percent_candidate.c','application_boot_power_samples_candidate.c','application_boot_current_sample_candidate.c']
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d); objs=[]
 for name in files:
  obj=d/(name+'.o');subprocess.run(flags+[str(src/name),'-o',str(obj)],check=True);objs.append(obj)
 stub=d/'stub.c';stub.write_text('''#include <stdint.h>
 int32_t case_policy_timer_query(uint32_t x,uint32_t *p){(void)x;(void)p;return 0;}
 int32_t case_init_pmic_read_register(uint32_t x,uint8_t *p){(void)x;(void)p;return 0;}
 uint32_t case_policy_sensor_divide(uint32_t x,uint32_t y){(void)x;(void)y;return 0;}
 ''');so=d/'stub.o';subprocess.run(flags+[str(stub),'-o',str(so)],check=True)
 elf=d/'sample.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',*[str(o) for o in objs],str(so),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 entries=[(0x9ebc,'case_boot_battery_percent'),(0x9f18,'case_boot_current_sample'),(0x9ff0,'case_boot_temperature_sample'),(0xa01e,'case_boot_battery_sample')]
 rng=random.Random(0x9ebc);n=0
 for off,name in entries:
  for i in range(96):
   raw=(i*8117+rng.randrange(65536))&0xffff;config=[0,1,0x40,0x80,0xc0][i%5];regfail=i%11==0;pin=(i%2); pairs=[]
   for native in (True,False):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,(len(firmware)+4095)&~4095);u.mem_write(0x08000000,firmware);u.mem_map(0x100000,0x10000)
    for a,b in segs:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20003000,struct.pack('<I',0xdeadbeef));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
    target={0x0800a074:'query',0x0800a124:'read'} if native else {symbols['case_policy_timer_query']&~1:'query',symbols['case_init_pmic_read_register']&~1:'read',symbols['case_policy_sensor_divide']&~1:'divide'}
    calls=[]
    def hook(uc,a,size,_):
     kind=target.get(a)
     if kind is None:return
     x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);calls.append((kind,x))
     if kind=='divide':uc.reg_write(UC_ARM_REG_R0,x//y)
     else:
      if kind=='query':uc.mem_write(y,struct.pack('<I',raw))
      else:uc.mem_write(y,bytes([config if x==0xab else raw&255]))
      uc.reg_write(UC_ARM_REG_R0,0xffffffff if regfail else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    def invalid(uc,access,address,size,value,user):print("INVALID",hex(off),native,i,hex(address),hex(uc.reg_read(UC_ARM_REG_PC)),calls);return False
    u.hook_add(UC_HOOK_MEM_INVALID,invalid)
    u.emu_start((0x08000000+off if native else symbols[name])|1,0x20008000,count=3000)
    pairs.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,4)),[(a,b) for a,b in calls if a!='divide']))
   assert pairs[0]==pairs[1],(hex(off),i,raw,config,regfail,pairs)
   n+=1
 print('PASS_CASE_POWER_SAMPLES',n)
