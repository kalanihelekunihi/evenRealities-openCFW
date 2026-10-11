#!/usr/bin/env python3
"""Native/source CASE sensor start/mode/clock at commit child cut."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_control_candidate.c';obj=H/'boot_sensor_control.oracle.o';stub=H/'boot_sensor_control.oracle_stub.c';stubobj=H/'boot_sensor_control.oracle_stub.o';elf=H/'boot_sensor_control.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_sensor_commit(uint32_t a){(void)a;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x5e2e)
for i in range(96):
 op=i%3;busy=i%11==0;option=rng.getrandbits(32);descriptor=[rng.getrandbits(32) for _ in range(40)];descriptor[0]=0x40013800;descriptor[33]=(descriptor[33]&~0xff)|(1 if busy else 0);hw=[rng.getrandbits(32) for _ in range(4)];pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
  u.mem_write(0x20003000,struct.pack('<40I',*descriptor));u.mem_write(0x40013800,struct.pack('<4I',*hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000);u.reg_write(UC_ARM_REG_R1,option)
  cut=0x0800856c if native else sym['case_boot_sensor_commit']&~1;trace=[]
  def hook(uc,a,size,_):
   if a==cut:trace.append((uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(0x40013800,12))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  address=([0x08005e2e,0x08005e6e,0x08005eb6][op] if native else sym[['case_boot_sensor_start','case_boot_sensor_set_clock','case_boot_sensor_set_mode'][op]])
  u.emu_start(address|1,0x20008000,count=1000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,160)),bytes(u.mem_read(0x40013800,16)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_SENSOR_CONTROL',96)
