#!/usr/bin/env python3
"""CASE 0x18e4 native/source periodic service policy at semantic child cuts."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_service_maintenance_candidate.c';obj=H/'service.oracle.o';stub=H/'service.oracle_stub.c';stubobj=H/'service.oracle_stub.o';elf=H/'service.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_log(uint32_t a,...){return a;}\nvoid case_policy_ota_checksum(uint8_t*a,uint32_t b){(void)a;(void)b;}\nuint32_t case_policy_send_probe(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_policy_parse_probe(uint32_t a){return a;}\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\n')
subprocess.run([x for x in flags if x not in ('-Wall','-Wextra','-Werror')]+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
orig={0x08009170:'log',0x08009b70:'crc',0x0800258c:'send',0x08001e94:'parse',0x08000160:'divide'}
srcs={sym['case_policy_log']&~1:'log',sym['case_policy_ota_checksum']&~1:'crc',sym['case_policy_send_probe']&~1:'send',sym['case_policy_parse_probe']&~1:'parse',sym['case_policy_sensor_divide']&~1:'divide'}
rng=random.Random(0x18e4)
for i in range(256):
 state=bytearray(rng.randbytes(128));state[0x10]=i%2;state[0x11]=(i//2)%2;state[0x31]=i%3==0;state[0x4d]=i%4==0;state[0x33]=i%5==0;state[0x4f]=i%7==0
 for o,v in ((0x0c,[0,5,20,21][i%4]),(0x44,[0,15,30,16][i%4]),(0x60,[0,15,30,16][(i//3)%4])):struct.pack_into('<I',state,o,v)
 for o,v in ((0x38,[0,30,60,31][i%4]),(0x54,[0,30,60,31][(i//4)%4])):struct.pack_into('<H',state,o,v)
 shared=i%3==0;quiet=i%5==0;parse_result=0x13 if i%3 else 0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x20000105,bytes([shared]));u.mem_write(0x200000bf,bytes([quiet]));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=orig if native else srcs;calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind=='divide':calls.append((kind,x,y));uc.reg_write(UC_ARM_REG_R0,x//y);uc.reg_write(UC_ARM_REG_R1,x%y)
   elif kind=='log':
    message=bytes(uc.mem_read(x,90)).split(b'\0')[0]
    calls.append((kind,message,y if message.startswith((b'L charging',b'R charging',b'L water',b'R water')) else None))
   elif kind=='crc':calls.append((kind,y,bytes(uc.mem_read(x,y))))
   elif kind=='send':calls.append((kind,x,z,w,bytes(uc.mem_read(y,z))))
   else:calls.append((kind,x));uc.reg_write(UC_ARM_REG_R0,parse_result)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x080018e4 if native else sym['case_policy_service_maintenance'])|1,0x20008000,count=5000)
  pair.append((calls,bytes(u.mem_read(0x2000087c,128))))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SERVICE_MAINTENANCE',256)
