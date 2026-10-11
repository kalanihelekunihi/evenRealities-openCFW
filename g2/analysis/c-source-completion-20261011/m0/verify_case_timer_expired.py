#!/usr/bin/env python3
"""CASE b0fc stock/C one-message timer queue drain oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_timer_expired_candidate.c';obj=H/'timer_expired.oracle.o';stub=H/'timer_expired.oracle_stub.c';stubobj=H/'timer_expired.oracle_stub.o';elf=H/'timer_expired.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_timer_command_receive(uint32_t a,uint32_t *b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\nvoid case_policy_task_unlink(uint32_t a){(void)a;}\nuint32_t case_boot_timer_now(uint32_t *x){*x=0;return 0;}\nuint32_t case_boot_timer_insert(uint32_t a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_policy_task_event_send(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 1;}\nvoid case_boot_heap_free(uint32_t a){(void)a;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xb0fc)
for i in range(224):
 command=([0xffffffff]+list(range(12)))[i%13];when=(rng.getrandbits(8)+1);now=rng.getrandbits(8);period=rng.getrandbits(8)+1;state=rng.getrandbits(8);insert_result=i%2;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000164,struct.pack('<I',0x20004000));u.mem_write(0x20002014,struct.pack('<I',i%3==0));u.mem_write(0x20002018,struct.pack('<I',period));u.mem_write(0x20002020,struct.pack('<I',0x08005f43));u.mem_write(0x20002028,bytes([state]))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x0800c83a:'receive',0x0800bf2c:'unlink',0x0800b284:'now',0x0800b024:'insert',0x0800cd80:'send',0x0800c030:'free',0x08005f42:'callback'} if native else {sym['case_boot_timer_command_receive']&~1:'receive',sym['case_policy_task_unlink']&~1:'unlink',sym['case_boot_timer_now']&~1:'now',sym['case_boot_timer_insert']&~1:'insert',sym['case_policy_task_event_send']&~1:'send',sym['case_boot_heap_free']&~1:'free',0x08005f42:'callback'})
  calls=[];count=[0]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
   if kind=='receive':
    if count[0]==0:
     msg=(command,0x08005f43 if command&0x80000000 else when,0x20002000,0x12345678)
     uc.mem_write(r1,struct.pack('<4I',*msg));uc.reg_write(UC_ARM_REG_R0,1)
    else:uc.reg_write(UC_ARM_REG_R0,0)
    count[0]+=1;calls.append(('receive',))
   elif kind=='now':uc.mem_write(r0,struct.pack('<I',0));uc.reg_write(UC_ARM_REG_R0,now);calls.append(('now',))
   elif kind=='insert':uc.reg_write(UC_ARM_REG_R0,insert_result);calls.append(('insert',r0,r1,r2,r3))
   elif kind=='send':uc.reg_write(UC_ARM_REG_R0,1);calls.append(('send',r0,r1,r2,r3))
   else:calls.append((kind,r0));uc.reg_write(UC_ARM_REG_R0,0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800b0fc if native else sym['case_boot_timer_expired'])|1,0x20008000,count=350)
  pair.append((calls,bytes(u.mem_read(0x20002000,0x30))))
 assert pair[0]==pair[1],(i,command,when,now,period,state,pair[0][0],pair[1][0])
print('PASS_CASE_TIMER_EXPIRED',224)
