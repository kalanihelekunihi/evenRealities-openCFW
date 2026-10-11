#!/usr/bin/env python3
"""Bounded CASE 0x258c stock/C packet send and framed-reply oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_send_probe_candidate.c'
obj=H/'send_probe.oracle.o';stub=H/'send_probe.oracle_stub.c';stubobj=H/'send_probe.oracle_stub.o';elf=H/'send_probe.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_policy_sensor_prepare(void){}\nuint32_t case_policy_sensor_shutdown(uint32_t x){return x;}\nvoid case_boot_sensor_service_start(void){}\nvoid case_control_write(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nvoid case_policy_ota_left_prepare(void){}\nvoid case_policy_ota_right_prepare(void){}\nint32_t case_policy_sensor_delay(uint32_t x){return (int32_t)x;}\nuint32_t case_boot_sensor_send_packet(const uint8_t *p,uint32_t n){return (uint32_t)(uintptr_t)p+n;}\nvoid case_boot_sensor_post_transmit(void){}\nuint32_t case_boot_sensor_finish_guard(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nvoid log_hex_buffer(const uint8_t*b,uint32_t n){(void)b;(void)n;}\nuint32_t case_policy_sensor_divide(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}\nuint32_t case_policy_log(uint32_t x){return x;}\nuint32_t case_policy_log_number(uint32_t x,uint32_t y){return x+y;}\nvoid case_policy_idle_clear(void){}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x258c)
for i in range(384):
 side=i%2;reply=i%3!=0;quiet=i%4==0;active=i%5==0
 index=rng.choice([0,1,2,3,4,5]);first_result=3 if i%9==0 else 0;extra_result=3 if i%11==0 else 0;data_result=3 if i%13==0 else 0
 sample=bytearray(rng.randrange(256) for _ in range(5));sample[3]=rng.randrange(16)
 if index<5:sample[index]=0x5a
 else:sample=bytearray(x if x!=0x5a else 0x59 for x in sample)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,bytes([0x3e,0,0,1,1,0]));u.mem_write(0x200000bf,bytes([int(quiet)]));u.mem_write(0x20000f40,struct.pack('<II',0x20 if active else 0,0))
  u.reg_write(UC_ARM_REG_R0,side);u.reg_write(UC_ARM_REG_R1,0x20002000);u.reg_write(UC_ARM_REG_R2,6);u.reg_write(UC_ARM_REG_R3,int(reply));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  names={'prepare':'case_policy_sensor_prepare','start':'case_boot_sensor_service_start','write':'case_control_write','left':'case_policy_ota_left_prepare','right':'case_policy_ota_right_prepare','delay':'case_policy_sensor_delay','send':'case_boot_sensor_send_packet','post':'case_boot_sensor_post_transmit','guard':'case_boot_sensor_finish_guard','hex':'log_hex_buffer','divide':'case_policy_sensor_divide','log':'case_policy_log','logn':'case_policy_log_number','shutdown':'case_policy_sensor_shutdown','idle':'case_policy_idle_clear'}
  targets=({0x0800d250:'prepare',0x08006cf8:'start',0x08004e9e:'write',0x0800be90:'left',0x0800bede:'right',0x0800a7b0:'delay',0x08003bb0:'send',0x08006c80:'post',0x080063ec:'guard',0x080067c8:'hex',0x08000160:'divide',0x08009170:'log',0x08005f00:'shutdown',0x08009a14:'idle'} if native else {sym[v]&~1:k for k,v in names.items()})
  calls=[];guard_count=[0]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1);z=uc.reg_read(UC_ARM_REG_R2);w=uc.reg_read(UC_ARM_REG_R3)
   if kind=='guard':
    k=guard_count[0];guard_count[0]+=1
    result=[first_result,extra_result,data_result][min(k,2)]
    if k==0 and result!=3:uc.mem_write(y,bytes(sample))
    if k>0 and result!=3:uc.mem_write(y,bytes((j+1)&255 for j in range(z)))
    calls.append((kind,x,y,z,w,result));uc.reg_write(UC_ARM_REG_R0,result)
   elif kind=='log' or kind=='logn':calls.append(('log',bytes(uc.mem_read(x,90)).split(b'\0')[0],y if x==0x08002720 else None))
   elif kind=='hex':calls.append((kind,y,bytes(uc.mem_read(x,y))))
   elif kind=='divide':calls.append((kind,x,y));uc.reg_write(UC_ARM_REG_R0,x//y)
   elif kind=='send':calls.append((kind,x,y,bytes(uc.mem_read(x,y))))
   else:calls.append((kind,x,y,z if kind=='write' else None))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800258c if native else sym['case_policy_send_probe'])|1,0x20008000,count=6000)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000664,32)),bytes(u.mem_read(0x200000bc,4))))
 assert pair[0]==pair[1],(i,side,reply,quiet,active,index,first_result,extra_result,data_result,pair[0][0],pair[1][0])
print('PASS_CASE_SEND_PROBE',384)
