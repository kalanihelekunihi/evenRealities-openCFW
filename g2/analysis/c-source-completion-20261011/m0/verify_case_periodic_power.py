#!/usr/bin/env python3
"""CASE 0x2a68 periodic power update native/source at four provider cuts."""
from pathlib import Path
import random,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_periodic_power_update_candidate.c'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'source.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 st=d/'stub.c';st.write_text('''#include <stdint.h>
 uint32_t case_init_pin_read(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
 uint32_t case_init_pmic_read(uint32_t a,uint8_t *b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
 void case_init_boost_set(uint32_t a){(void)a;}
 uint32_t case_policy_log(uint32_t a,...){(void)a;return 0;}
 ''');so=d/'stub.o';subprocess.run(flags+[str(st),'-o',str(so)],check=True)
 elf=d/'out.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),str(so),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 native={0x08004e94:'pin',0x080035d4:'read',0x08002c30:'boost',0x08009170:'log'}
 source={sym['case_init_pin_read']&~1:'pin',sym['case_init_pmic_read']&~1:'read',sym['case_init_boost_set']&~1:'boost',sym['case_policy_log']&~1:'log'}
 rng=random.Random(0x2a68)
 for i in range(192):
  pin=i&1;bit=(i>>1)&1;state=(i>>2)&1;count=[0,1,2,3,255][i%5];quiet=(i>>3)&1;pairs=[]
  for original in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
   for a,b in seg:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087f,bytes([state]));u.mem_write(0x20000028,bytes([count]));u.mem_write(0x200000bf,bytes([quiet]));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
   target=native if original else source;calls=[]
   def hook(uc,a,size,_):
    kind=target.get(a)
    if kind is None:return
    x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2)
    if kind=='pin':calls.append((kind,x,y));uc.reg_write(UC_ARM_REG_R0,pin)
    elif kind=='read':calls.append((kind,x,z));uc.mem_write(y,bytes([bit]));uc.reg_write(UC_ARM_REG_R0,0)
    elif kind=='boost':calls.append((kind,x))
    else:calls.append((kind,bytes(uc.mem_read(x,8))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08002a68 if original else sym['case_boot_periodic_power_update'])|1,0x20008000,count=3000)
   pairs.append((bytes(u.mem_read(0x2000087c,8)),bytes(u.mem_read(0x20000028,1)),calls))
  assert pairs[0]==pairs[1],(i,pin,bit,state,count,quiet,pairs)
 print('PASS_CASE_PERIODIC_POWER',192)
