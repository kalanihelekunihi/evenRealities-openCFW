#!/usr/bin/env python3
"""Bounded native/C 0x3bb0 descriptor-bound packet wrapper oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_send_packet_candidate.c'
obj=H/'sensor_send_packet.oracle.o';stub=H/'sensor_send_packet.oracle_stub.c';stubobj=H/'sensor_send_packet.oracle_stub.o';elf=H/'sensor_send_packet.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_sensor_transfer(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){return a+(uint32_t)(uintptr_t)b+c+d;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x3bb0)
for i in range(128):
 ptr=rng.choice([0,0x20002000,0x20003000]);count=rng.choice([0,1,5,6,255,65535]);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_R0,ptr);u.reg_write(UC_ARM_REG_R1,count);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  target=0x080066ac if native else sym['case_boot_sensor_transfer']&~1;calls=[]
  def hook(uc,a,n,_):
   if a!=target:return
   calls.append(tuple(uc.reg_read(q) for q in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]));uc.reg_write(UC_ARM_REG_R0,37);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08003bb0 if native else sym['case_boot_sensor_send_packet'])|1,0x20008000,count=500)
  pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(i,ptr,count,pair)
print('PASS_CASE_SENSOR_SEND_PACKET',128)
