#!/usr/bin/env python3
"""CASE 0x66ac native/source transfer through real descriptor and MMIO at ready-child cut."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
S=R/'g2/components/case/startup_candidate_20261011';srcs=[S/'application_boot_sensor_transfer_candidate.c',S/'application_policy_adc_register_candidate.c'];objs=[H/'sensor_transfer.oracle.o',H/'sensor_transfer_tick.oracle.o'];stub=H/'sensor_transfer.oracle_stub.c';stubobj=H/'sensor_transfer.oracle_stub.o';elf=H/'sensor_transfer.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
for s,o in zip(srcs,objs):subprocess.run(flags+[str(s),'-o',str(o)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_sensor_open_ready(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x66ac)
for i in range(192):
 desc=bytearray(rng.randbytes(160));hw=bytearray(rng.randbytes(48));data=bytearray(rng.randbytes(32));struct.pack_into('<I',desc,0,0x40013800)
 struct.pack_into('<I',desc,136,32 if i%7 else 34);struct.pack_into('<I',desc,8,[0,0x1000,0x10000000,0x3000][i%4]);struct.pack_into('<I',desc,16,0 if i%3 else 1)
 count=i%5;packet=0 if i%13==0 else 0x20004001 if i%2 else 0x20004000;timeout=rng.getrandbits(32);tick=rng.getrandbits(32)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
  u.mem_write(0x20000120,struct.pack('<I',tick));u.mem_write(0x20003000,bytes(desc));u.mem_write(0x20004000,bytes(data));u.mem_write(0x40013800,bytes(hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,packet);u.reg_write(UC_ARM_REG_R2,count);u.reg_write(UC_ARM_REG_R3,timeout)
  target=0x08008ec4 if native else sym['case_boot_sensor_open_ready']&~1;calls=[]
  def hook(uc,a,size,_):
   if a==target:
    regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3));fifth=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
    calls.append((*regs,fifth));uc.reg_write(UC_ARM_REG_R0,1 if i%11==0 else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080066ac if native else sym['case_boot_sensor_transfer'])|1,0x20008000,count=1500)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,160)),bytes(u.mem_read(0x40013800,48)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_SENSOR_TRANSFER',192)
