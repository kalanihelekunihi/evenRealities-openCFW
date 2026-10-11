#!/usr/bin/env python3
"""Bounded CASE 0x1c1c stock/C packet and reply-state oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_action_candidate.c'
obj=H/'transport_action.oracle.o';stub=H/'transport_action.oracle_stub.c';stubobj=H/'transport_action.oracle_stub.o';elf=H/'transport_action.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
template=F[0x1d04:0x1d0c]
stub.write_text('#include <stdint.h>\nconst uint8_t case_boot_transport_action_template[8]={'+','.join(str(x) for x in template)+'};\nvoid case_policy_ota_checksum(uint8_t *p,uint32_t n){(void)p;(void)n;}\nvoid case_policy_send_probe(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}\nuint32_t case_policy_parse_probe(uint32_t x){return x;}\nuint32_t case_policy_log(uint32_t x){return x;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x1c1c)
for i in range(256):
 state=bytearray(rng.randbytes(0x80));state[16]=rng.randrange(2);state[17]=rng.randrange(2);quiet=rng.randrange(2);left=i%3!=0;right=i%4!=0;reply=19 if i%2 else 0
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000bf,bytes([quiet]));u.reg_write(UC_ARM_REG_R0,int(left));u.reg_write(UC_ARM_REG_R1,int(right));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08009b70:'checksum',0x0800258c:'send',0x08001e94:'parse',0x08009170:'log'} if native else {sym['case_policy_ota_checksum']&~1:'checksum',sym['case_policy_send_probe']&~1:'send',sym['case_policy_parse_probe']&~1:'parse',sym['case_policy_log']&~1:'log'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind=='checksum':calls.append((kind,y,bytes(uc.mem_read(x,8))))
   elif kind=='send':calls.append((kind,x,z,w,bytes(uc.mem_read(y,8))))
   else:calls.append((kind,x))
   uc.reg_write(UC_ARM_REG_R0,reply if kind=='parse' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08001c1c if native else sym['case_boot_transport_action'])|1,0x20008000,count=3000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,0x80))))
 assert pair[0]==pair[1],(i,left,right,reply,pair[0][0],pair[1][0])
print('PASS_CASE_TRANSPORT_ACTION',256)
