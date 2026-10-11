#!/usr/bin/env python3
"""CASE 0x6308 two sensor hardware branches at clock/GPIO/IRQ child cuts."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_open_initialize_candidate.c';obj=H/'boot_sensor_init.oracle.o';stub=H/'boot_sensor_init.oracle_stub.c';stubobj=H/'boot_sensor_init.oracle_stub.o';elf=H/'boot_sensor_init.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_boot_bus_clock_setup(uint32_t *x){(void)x;return 0;}\n__attribute__((noreturn)) void case_boot_init_failure(void){for(;;){}}\nvoid case_bus_gpio_config(uint32_t x,volatile uint32_t *y){(void)x;(void)y;}\nvoid case_clock_priority_config(uint32_t x,uint32_t y,uint32_t z){(void)x;(void)y;(void)z;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x6308)
for i in range(96):
 base=[0x40013800,0x40004800,0x40005000][i%3];descriptor=bytearray(rng.randbytes(160));struct.pack_into('<I',descriptor,0,base)
 mmio=bytearray(rng.randbytes(0x100));pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_map(0xe000e000,0x1000)
  u.mem_write(0x20003000,bytes(descriptor));u.mem_write(0x40021000,bytes(mmio))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  targets=({0x08005128:'clock',0x08004d30:'gpio',0x08005024:'priority'} if native else {sym['case_boot_bus_clock_setup']&~1:'clock',sym['case_bus_gpio_config']&~1:'gpio',sym['case_clock_priority_config']&~1:'priority'})
  calls=[]
  def hook(uc,a,size,_):
   if a not in targets:return
   kind=targets[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
   item=(kind,bytes(uc.mem_read(r0,44))) if kind=='clock' else (kind,r0,bytes(uc.mem_read(r1,20))) if kind=='gpio' else (kind,r0,r1,r2) if kind=='priority' else (kind,r0)
   calls.append(item);uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08006308 if native else sym['case_boot_sensor_open_initialize'])|1,0x20008000,count=2000)
  pair.append((bytes(u.mem_read(0x40021000,0x100)),bytes(u.mem_read(0xe000e100,4)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_SENSOR_OPEN_INITIALIZE',96)
