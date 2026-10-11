#!/usr/bin/env python3
"""Native/C CASE pin initializer MMIO and child-call contract oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_pin_initialize_candidate.c';obj=H/'pin_initialize.oracle.o';stub=H/'pin_initialize.oracle_stub.c';stubobj=H/'pin_initialize.oracle_stub.o';elf=H/'pin_initialize.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_control_write(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nvoid case_bus_gpio_config(uint32_t a,volatile uint32_t *b){(void)a;(void)b;}\nvoid case_clock_priority_config(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\nvoid case_boot_sensor_irq_enable(uint32_t a){(void)a;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x6a40)
for i in range(64):
 clock=rng.getrandbits(32);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_map(0x50000000,0x1000)
  u.mem_write(0x40021034,struct.pack('<I',clock));u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08004e9e:'ctrl',0x08004d30:'gpio',0x08005024:'priority',0x0800500c:'enable'} if native else {sym['case_control_write']&~1:'ctrl',sym['case_bus_gpio_config']&~1:'gpio',sym['case_clock_priority_config']&~1:'priority',sym['case_boot_sensor_irq_enable']&~1:'enable'})
  calls=[]
  def hook(uc,a,size,_):
   kind=targets.get(a)
   if kind is None:return
   r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
   calls.append((kind,r0,struct.unpack('<4I',bytes(uc.mem_read(r1,16))) if kind=='gpio' else (r1,r2) if kind in ('ctrl','priority') else ()))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08006a40 if native else sym['case_boot_pin_initialize'])|1,0x20008000,count=1500)
  pair.append((calls,bytes(u.mem_read(0x40021034,4))))
 assert pair[0]==pair[1],(i,pair[0],pair[1])
print('PASS_CASE_PIN_INITIALIZE',64)
