#!/usr/bin/env python3
"""Native/source 0x99e8 cache, bus success and bus failure cases."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_idle_clear_candidate.c'
stub=H/'policy_sensor_command_oracle_stubs.c';stub.write_text('#include <stdint.h>\n__attribute__((noinline,used)) uint32_t case_policy_bus_write(uint32_t w,uint32_t a,uint32_t b,const uint8_t *c){(void)w;(void)a;(void)b;(void)c;__asm__ volatile("nop");return 0;}\n__attribute__((noinline,used)) void case_policy_log_four(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_log(uint32_t a){(void)a;__asm__ volatile("nop");}\n')
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.sensor_cmd.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_sensor_command_oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
checked=0
for channel,value,cache,response in itertools.product((0,3,4,5,6,7),(0,1,0xae,0xaf,0x181),(0,1,0xae,0xaf,0x81),(0,1)):
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000090+channel,bytes([cache]));u.mem_write(0x200000bf,b'\x01')
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,channel);u.reg_write(UC_ARM_REG_R1,value)
  calls=[];target=0x08000610 if native else sym['case_policy_bus_write']&~1
  def hook(u,a,size,ctx):
   if a==target:
    calls.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2),u.mem_read(u.reg_read(UC_ARM_REG_R3),1)[0]));u.reg_write(UC_ARM_REG_R0,response);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080099e8 if native else sym['case_policy_sensor_command'])|1,0x20001000,count=1000)
  pair.append((calls,bytes(u.mem_read(0x20000090,8))))
 assert pair[0]==pair[1],(channel,value,cache,response,pair)
 checked+=1
print('PASS_CASE_POLICY_SENSOR_COMMAND',checked)
