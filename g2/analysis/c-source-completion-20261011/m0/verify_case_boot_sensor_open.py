#!/usr/bin/env python3
"""Native/source sensor open at its four real child cuts."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_open_candidate.c';obj=H/'boot_sensor_open.oracle.o';stub=H/'boot_sensor_open.oracle_stub.c';stubobj=H/'boot_sensor_open.oracle_stub.o';elf=H/'boot_sensor_open.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_sensor_open_initialize(uint32_t x){(void)x;}\nuint32_t case_boot_sensor_open_validate(uint32_t x){(void)x;return 0;}\nvoid case_boot_sensor_open_apply(uint32_t x){(void)x;}\nuint32_t case_boot_sensor_open_finish(uint32_t x){(void)x;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x6240)
for i in range(96):
 desc=bytearray(rng.randbytes(160));hw=bytearray(rng.randbytes(48));struct.pack_into('<I',desc,0,0x40013800)
 struct.pack_into('<I',desc,136,0 if i%3==0 else 32)
 struct.pack_into('<I',desc,40,0 if i%4==0 else 0x100)
 answer=1 if i%5==0 else (2 if i%7==0 else 0);final=i%4
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
  u.mem_write(0x20003000,bytes(desc));u.mem_write(0x40013800,bytes(hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0 if i%13==0 else 0x20003000)
  targets=({0x08006308:'init',0x08008bd8:'validate',0x080085b0:'apply',0x0800867c:'finish'} if native else {sym['case_boot_sensor_open_initialize']&~1:'init',sym['case_boot_sensor_open_validate']&~1:'validate',sym['case_boot_sensor_open_apply']&~1:'apply',sym['case_boot_sensor_open_finish']&~1:'finish'})
  calls=[]
  def hook(uc,a,size,_):
   if a in targets:
    kind=targets[a];calls.append((kind,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_R0,answer if kind=='validate' else final if kind=='finish' else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08006240 if native else sym['case_boot_sensor_open'])|1,0x20008000,count=1000)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,160)),bytes(u.mem_read(0x40013800,48)),calls))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_SENSOR_OPEN',96)
