#!/usr/bin/env python3
"""Bounded stock/C CASE 0x23f4/0x24c0 request/state oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_aging_control_candidate.c'
obj=H/'aging_control.oracle.o';stub=H/'aging_control.oracle_stub.c';stubobj=H/'aging_control.oracle_stub.o';elf=H/'aging_control.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_ota_checksum(uint8_t *p,uint32_t n){(void)p;(void)n;}\nvoid case_policy_send_probe(uint32_t s,const uint8_t *p,uint32_t n,uint32_t q){(void)s;(void)p;(void)n;(void)q;}\nuint32_t case_policy_parse_probe(uint32_t s){return s;}\nuint32_t case_policy_log(uint32_t x){return x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x23f4)
for i in range(384):
 side=i%2;enabled=rng.randrange(2);present=rng.randrange(2);busy=rng.randrange(2);quiet=rng.randrange(2);response=rng.choice([62,0,19,255])
 state=bytearray(0x40);state[16 if side else 17]=present;device=bytearray(0x10);device[2 if side else 3]=rng.randrange(2)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000f4,bytes(device));u.mem_write(0x200000bc,bytes([busy,0,0,quiet]))
  u.reg_write(UC_ARM_REG_R0,enabled);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08009b70:'checksum',0x0800258c:'send',0x08001e94:'parse',0x08009170:'log'} if native else {sym['case_policy_ota_checksum']&~1:'checksum',sym['case_policy_send_probe']&~1:'send',sym['case_policy_parse_probe']&~1:'parse',sym['case_policy_log']&~1:'log'})
  calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind=='checksum':
    p=bytearray(uc.mem_read(x,y));p[y-1]=(y+125+sum(p[:-1]))&255;uc.mem_write(x,bytes(p));calls.append(('checksum',y,bytes(p)))
   elif kind=='send':calls.append(('send',x,z,w,bytes(uc.mem_read(y,z))))
   elif kind=='parse':calls.append(('parse',x));uc.reg_write(UC_ARM_REG_R0,response)
   else:calls.append(('log',bytes(uc.mem_read(x,80)).split(b'\0')[0]))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(((0x080023f4 if side else 0x080024c0) if native else sym['case_boot_transport_left_aging' if side else 'case_boot_transport_right_aging'])|1,0x20008000,count=2000)
  pair.append((calls,bytes(u.mem_read(0x200000bc,4)),bytes(u.mem_read(0x200000f4,0x10))))
 assert pair[0]==pair[1],(i,side,enabled,present,busy,quiet,response,pair)
print('PASS_CASE_AGING_CONTROL',384)
