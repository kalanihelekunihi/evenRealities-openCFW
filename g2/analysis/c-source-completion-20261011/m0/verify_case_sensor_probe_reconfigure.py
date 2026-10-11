#!/usr/bin/env python3
"""Bounded stock/C CASE 0x6c80/0x6cf8 descriptor and child-order oracle."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_probe_reconfigure_candidate.c'
obj=H/'sensor_reconfigure.oracle.o';stub=H/'sensor_reconfigure.oracle_stub.c';stubobj=H/'sensor_reconfigure.oracle_stub.o';elf=H/'sensor_reconfigure.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nuint32_t case_policy_sensor_shutdown(uint32_t x){return x;}\nuint32_t case_boot_sensor_open(uint32_t x){return x;}\nuint32_t case_boot_sensor_set_mode(uint32_t a,uint32_t b){return a+b;}\nuint32_t case_boot_sensor_set_clock(uint32_t a,uint32_t b){return a+b;}\nuint32_t case_boot_sensor_start(uint32_t x){return x;}\n__attribute__((noreturn)) void case_boot_init_failure(void){for(;;);}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x6c80)
for i in range(256):
 mode=i%2;before=bytes(rng.randrange(256) for _ in range(0xa0));pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000eb8,before);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  targets=({0x08005f00:'shutdown',0x08006240:'open',0x08005eb6:'mode',0x08005e6e:'clock',0x08005e2e:'start',0x08003e90:'failure'} if native else {sym['case_policy_sensor_shutdown']&~1:'shutdown',sym['case_boot_sensor_open']&~1:'open',sym['case_boot_sensor_set_mode']&~1:'mode',sym['case_boot_sensor_set_clock']&~1:'clock',sym['case_boot_sensor_start']&~1:'start',sym['case_boot_init_failure']&~1:'failure'})
  calls=[]
  def hook(uc,a,n,_):
   kind=targets.get(a)
   if kind is None:return
   calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if kind in ('mode','clock') else None))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(((0x08006c80 if mode==0 else 0x08006cf8) if native else sym['case_boot_sensor_post_transmit' if mode==0 else 'case_boot_sensor_service_start'])|1,0x20008000,count=2000)
  pair.append((calls,bytes(u.mem_read(0x20000eb8,0xa0))))
 assert pair[0]==pair[1],(i,mode,pair[0][0],pair[1][0])
print('PASS_CASE_SENSOR_PROBE_RECONFIGURE',256)
