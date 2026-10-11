#!/usr/bin/env python3
"""Compare CASE 0x867c readiness/finish at the 0x8ec4 child cut."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011';srcs=[S/'application_boot_sensor_open_finish_candidate.c',S/'application_policy_adc_register_candidate.c']
objs=[H/'boot_sensor_finish.oracle.o',H/'boot_sensor_tick.oracle.o'];stub=H/'boot_sensor_finish.oracle_stub.c';stubobj=H/'boot_sensor_finish.oracle_stub.o';elf=H/'boot_sensor_finish.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
for s,o in zip(srcs,objs):subprocess.run(flags+[str(s),'-o',str(o)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_sensor_open_ready(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x867c)
for i in range(96):
 desc=bytearray(rng.randbytes(160));hw=bytearray(rng.randbytes(48));struct.pack_into('<I',desc,0,0x40013800);control=rng.getrandbits(32);control=(control&~12)|((i%4)<<2);struct.pack_into('<I',hw,0,control)
 tick=rng.getrandbits(32);answer=1 if i%7==0 else 0;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
  u.mem_write(0x20000120,struct.pack('<I',tick));u.mem_write(0x20003000,bytes(desc));u.mem_write(0x40013800,bytes(hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  target=0x08008ec4 if native else sym['case_boot_sensor_open_ready']&~1;calls=[]
  def hook(uc,a,size,_):
   if a==target:
    regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    fifth=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
    calls.append((*regs,fifth));uc.reg_write(UC_ARM_REG_R0,answer);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800867c if native else sym['case_boot_sensor_open_finish'])|1,0x20008000,count=1500)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,160)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_SENSOR_OPEN_FINISH',96)
