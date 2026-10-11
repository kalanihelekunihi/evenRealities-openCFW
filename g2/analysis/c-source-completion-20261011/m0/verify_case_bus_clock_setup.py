#!/usr/bin/env python3
"""Bounded original/C MMIO comparison for CASE 0x5128 non-wait paths."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_bus_clock_setup_candidate.c'
obj=H/'bus_clock_setup.oracle.o';stub=H/'bus_clock_setup.oracle_stub.c';stubobj=H/'bus_clock_setup.oracle_stub.o';elf=H/'bus_clock_setup.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_adc_tick(void){return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x5128)
for i in range(128):
 config=[rng.getrandbits(32) for _ in range(11)]
 config[0]=[0,1,2,4,0x20,0x40,0x800,0x2000,0x4000,0x1000000][i%10]
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40007000,0x1000);u.mem_map(0x40021000,0x1000)
  u.mem_write(0x20003000,struct.pack('<11I',*config));u.mem_write(0x40021000,bytes(rng.randrange(256) for _ in range(0x80)))
  # Use a fixed MMIO baseline for both runs.
  if native:baseline=bytes(u.mem_read(0x40021000,0x80))
  else:u.mem_write(0x40021000,baseline)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  target=0x08004eac if native else sym['case_policy_adc_tick']&~1
  def hook(uc,a,size,_):
   if a==target:uc.reg_write(UC_ARM_REG_R0,100);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08005128 if native else sym['case_boot_bus_clock_setup'])|1,0x20008000,count=3000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x40021000,0x80))))
 assert pair[0]==pair[1],(i,hex(config[0]),pair[0][0],pair[1][0],[(x,a,b) for x,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b][:8])
print('PASS_CASE_BUS_CLOCK_SETUP',128)
