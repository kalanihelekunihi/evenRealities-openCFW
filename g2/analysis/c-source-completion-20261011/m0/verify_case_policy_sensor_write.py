#!/usr/bin/env python3
"""Original/source 0x9108 IRQ-guarded retry and failure logging."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_idle_clear_candidate.c'
stub=H/'policy_sensor_write_oracle_stubs.c';stub.write_text('#include <stdint.h>\n__attribute__((noinline,used)) uint32_t case_policy_bus_write(uint32_t a,uint32_t b,uint32_t c,const uint8_t *d){(void)a;(void)b;(void)c;(void)d;__asm__ volatile("nop");return 0;}\n__attribute__((noinline,used)) void case_policy_log_four(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_log(uint32_t a){(void)a;__asm__ volatile("nop");}\n')
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.sensor_write.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_sensor_write_oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
checked=0
for first_success,debug,seed in itertools.product((1,2,5,9,10),(0,1),(0,0x1234)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x20000080,seed.to_bytes(4,'little'));u.mem_write(0x20000084,(0x12345678).to_bytes(4,'little'));u.mem_write(0x20000088,(0x9abcdef0).to_bytes(4,'little'));u.mem_write(0x2000008c,(0x10203040).to_bytes(4,'little'));u.mem_write(0x200000bf,bytes([debug]));u.mem_write(0x20001000,b'\xa5')
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20002001);u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_R1,1);u.reg_write(UC_ARM_REG_R2,0x20001000)
  bus=0;calls=[]
  lookup=({0x08000610:'bus',0x08009170:'log'} if native else {sym['case_policy_bus_write']&~1:'bus',sym['case_policy_log_four']&~1:'log4',sym['case_policy_log']&~1:'log1'})
  def hook(u,a,size,ctx):
   nonlocal_bus[0]+=1 if a in lookup and lookup[a]=='bus' else 0
   if a not in lookup:return
   kind=lookup[a];r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);r2=u.reg_read(UC_ARM_REG_R2);r3=u.reg_read(UC_ARM_REG_R3)
   if kind=='bus':
    calls.append(('bus',r0,r1,r2,u.mem_read(r3,1)[0]));u.reg_write(UC_ARM_REG_R0,7 if nonlocal_bus[0]==first_success else 0)
   elif kind=='log4' or (kind=='log' and r0==0x0800d538):
    calls.append(('log4',r0,r1,r2,r3,int.from_bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4),'little')))
   else:calls.append(('log1',r0))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  nonlocal_bus=[0]
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08009108 if native else sym['case_policy_sensor_write'])|1,0x20002000,count=10000)
  pair.append((calls,int.from_bytes(u.mem_read(0x20000080,4),'little'),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(first_success,debug,seed,pair)
 checked+=1
print('PASS_CASE_POLICY_SENSOR_WRITE',checked)
