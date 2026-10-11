#!/usr/bin/env python3
"""Control-boundary oracle for OTA probe; packet product bytes stay unresolved."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_ota_probe_candidate.c'
stub=H/'policy_ota_probe_oracle_stubs.c'
stub.write_text('#include <stdint.h>\n/* Synthetic oracle-only data; no stock payload is copied. */\nconst uint8_t case_policy_ota_probe_template[12]={0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a,0xa5,0x5a};\n__attribute__((noinline,used)) void case_policy_log(uint32_t x){(void)x;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_wait(uint32_t x){(void)x;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_send_probe(uint32_t x,const uint8_t *y,uint32_t z){(void)x;(void)y;(void)z;__asm__ volatile("nop");}\n__attribute__((noinline,used)) void case_policy_parse_probe(uint32_t x){(void)x;__asm__ volatile("nop");}\n')
objs=[]
for s in (src,stub):
 o=H/(s.stem+'.oracle.o');objs.append(o)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
elf=H/'policy_ota_probe_oracle.elf'
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(o) for o in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
cases=itertools.product((0,1),(0,1),(20,21),(50,51),(20,21),(0,1),(0,1),(0,1))
checked=0
for sl,sr,secs,signal,age,done,busy,silent in cases:
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x2000088c,bytes([sl,sr]));u.mem_write(0x20000888,secs.to_bytes(4,'little'));u.mem_write(0x200008ae,bytes([signal]));u.mem_write(0x2000087d,bytes([age]));u.mem_write(0x20000897,bytes([done]));u.mem_write(0x200000bc,bytes([busy]));u.mem_write(0x200000bf,bytes([silent]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
  if native:
   u.reg_write(UC_ARM_REG_R4,0x2000087c);u.mem_write(0x20007fc4,(0x2000089c).to_bytes(4,'little'))
  else:u.reg_write(UC_ARM_REG_R0,0x2000087c);u.reg_write(UC_ARM_REG_R1,0x2000089c)
  calls=[];lookup=({0x08009170:'log',0x0800a7b0:'wait',0x0800258c:'send',0x08001e94:'parse'} if native else {sym['case_policy_log']&~1:'log',sym['case_policy_wait']&~1:'wait',sym['case_policy_send_probe']&~1:'send',sym['case_policy_parse_probe']&~1:'parse'})
  def hook(u,a,size,ctx):
   if native and a==0x08007b2e:u.emu_stop();return
   if a in lookup:
    kind=lookup[a];r0=u.reg_read(UC_ARM_REG_R0)
    calls.append((kind,r0,u.reg_read(UC_ARM_REG_R2)) if kind=='send' else (kind,r0))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08007abc if native else sym['case_policy_ota_probe_7abc'])|1,0x20001000,count=10000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x20)),bytes(u.mem_read(0x200000b8,8)),u.reg_read(UC_ARM_REG_R0) if not native else 0))
 a,b=pair
 assert a[:3]==b[:3],(sl,sr,secs,signal,age,done,busy,silent,a,b)
 assert b[3]==(1 if ('send',1,9) in a[0] else 0),(sl,sr,secs,signal,age,done,busy,silent,a,b)
 checked+=1
print('PASS_CASE_POLICY_OTA_PROBE_CONTROL',checked,'PRODUCT_PACKET_UNQUALIFIED')
