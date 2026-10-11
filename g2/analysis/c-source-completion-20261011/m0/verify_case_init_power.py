#!/usr/bin/env python3
"""Native/source initialization power call traces at lower cuts."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_init_power_candidate.c';obj=H/'application_init_power.oracle.o';stub=H/'application_init_power.oracle_stub.c';stubobj=H/'application_init_power.oracle_stub.o';elf=H/'application_init_power.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nint32_t case_init_pmic_probe_once(void){return 0;}\nvoid case_init_pmic_reset(uint32_t a,uint32_t b){(void)a;(void)b;}\nuint32_t case_init_pmic_read(uint32_t a,uint8_t*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\nuint32_t case_init_secondary_write(uint32_t a,uint32_t b,const uint8_t*c){(void)a;(void)b;(void)c;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x2c30)
for i in range(120):
 name,entry=('prepare',0x9df4) if i%3==0 else (('boost',0x2c30) if i%3==1 else ('power',0x2c8e));enabled=(i//3)&1;success=(i//6)%4;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,enabled)
  cuts=({0x0800a046:'probe',0x080039e4:'reset',0x080035d4:'read',0x08009004:'write'} if native else {sym['case_init_pmic_probe_once']&~1:'probe',sym['case_init_pmic_reset']&~1:'reset',sym['case_init_pmic_read']&~1:'read',sym['case_init_secondary_write']&~1:'write'})
  trace=[]
  def hook(uc,a,size,_):
   k=cuts.get(a)
   if k is None:return
   if k=='probe':
    n=sum(t[0]=='probe' for t in trace);trace.append((k,));uc.reg_write(UC_ARM_REG_R0,0 if n==success else -1&0xffffffff)
   elif k=='reset':trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   elif k=='read':
    n=sum(t[0]=='read' for t in trace);trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2)))
    uc.mem_write(uc.reg_read(UC_ARM_REG_R1),bytes(((9 if enabled else 8) if n==success else 0,)))
   else:trace.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.mem_read(uc.reg_read(UC_ARM_REG_R2),1)[0]))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  source={'prepare':'case_init_pmic_prepare','boost':'case_init_boost_set','power':'case_init_power_set'}[name]
  u.emu_start((0x08000000+entry if native else sym[source])|1,0x20008000,count=500)
  pair.append(trace)
 assert pair[0]==pair[1],(i,name,pair)
print('PASS_CASE_INIT_POWER',120)
