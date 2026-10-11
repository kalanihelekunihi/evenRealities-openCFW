#!/usr/bin/env python3
"""Bounded stock/C CASE 0xbb90 transport confirmation oracle with child cuts."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_transport_cb_bb90_candidate.c'
obj=H/'transport_confirmation.oracle.o';stub=H/'transport_confirmation.oracle_stub.c';stubobj=H/'transport_confirmation.oracle_stub.o';elf=H/'transport_confirmation.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_log(uint32_t x){return x;}\nuint32_t case_policy_log_four(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){return a+b+c+d+e;}\nvoid case_boot_irq_hall_prepare(uint32_t x){(void)x;}\nint32_t case_policy_event_signal(uint32_t a,uint32_t b){return a+b;}\nint32_t case_policy_task_reset(uint32_t a){return a;}\nint32_t case_boot_sensor_finish_signal(uint32_t a,uint32_t b){return a+b;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xbb90)
for i in range(768):
 state=bytearray(0x100);shared=bytearray(0x80)
 for j in [16,17,48,52,76,80]:state[j]=rng.choice([0,1,2])
 state[0]=rng.choice([0,1,3]);state[2]=rng.randrange(5);state[20]=rng.randrange(4);shared[7]=rng.randrange(2)
 state[68:72]=struct.pack('<I',rng.choice([0,209,210,211]));state[96:100]=struct.pack('<I',rng.choice([0,209,210,211]))
 for a in [16,24,56]:shared[a:a+4]=struct.pack('<I',0x12340000+a+i)
 pair=[];traces=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x2000087c,bytes(state));u.mem_write(0x200000b8,bytes(shared))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08009170:'log',0x08003848:'hall',0x0800aaf0:'event',0x0800ab26:'reset',0x0800a888:'finish'} if native else {sym['case_policy_log']&~1:'log',sym['case_policy_log_four']&~1:'log',sym['case_boot_irq_hall_prepare']&~1:'hall',sym['case_policy_event_signal']&~1:'event',sym['case_policy_task_reset']&~1:'reset',sym['case_boot_sensor_finish_signal']&~1:'finish'})
  calls=[];visited=[]
  def hook(uc,a,n,_):
   if i==5 and native and 0x0800bb90<=a<0x0800bd08:visited.append(hex(a))
   kind=targets.get(a)
   if kind is None:return
   x=uc.reg_read(UC_ARM_REG_R0);y=uc.reg_read(UC_ARM_REG_R1)
   calls.append((kind,bytes(uc.mem_read(x,120)).split(b'\0')[0] if kind=='log' else x,y if kind in ('event','finish') else None))
   uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800bb90 if native else sym['case_boot_transport_cb_bb90'])|1,0x20008000,count=3000)
  traces.append(visited)
  pair.append((calls,bytes(u.mem_read(0x200000b8,0x80)),bytes(u.mem_read(0x2000087c,0x100))))
 assert pair[0]==pair[1],(i, state[16],state[17],state[2],state[48],state[52],state[76],state[80],struct.unpack('<I',state[68:72])[0],struct.unpack('<I',state[96:100])[0],pair[0][0],pair[1][0],traces[0] if i==5 else '')
print('PASS_CASE_TRANSPORT_CONFIRMATION',768)
