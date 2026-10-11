#!/usr/bin/env python3
"""Native/source CASE 0x5a74 bus open at reset/prepare/apply child cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_bus_open_candidate.c';obj=H/'boot_bus_open.oracle.o';stub=H/'boot_bus_open.oracle_stub.c';stubobj=H/'boot_bus_open.oracle_stub.o';elf=H/'boot_bus_open.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nvoid case_boot_bus_reset(uint32_t a){(void)a;}\nuint32_t case_boot_bus_prepare(uint32_t a){(void)a;return 0;}\nuint32_t case_boot_bus_apply(uint32_t a){(void)a;return 0;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x5a74)
for i in range(96):
 d=0 if i%17==0 else 0x20003000;initial=[rng.getrandbits(32) for _ in range(11)];initial[0]=0x40002800;initial[10]=rng.choice([0,1,2])<<8;hw=[rng.getrandbits(32) for _ in range(10)];hw[3]=(hw[3]&~16)|(16 if i%5==0 else 0);fail=i%7;pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40002000,0x1000)
  u.mem_write(0x20003000,struct.pack('<11I',*initial));u.mem_write(0x40002800,struct.pack('<10I',*hw))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,d)
  names=['case_boot_bus_reset','case_boot_bus_prepare','case_boot_bus_apply'];cuts=({0x08005b24:names[0],0x08006d72:names[1],0x08006db8:names[2]} if native else {sym[n]&~1:n for n in names});trace=[]
  def hook(uc,a,size,_):
   if a in cuts:
    n=cuts[a];trace.append((n,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_R0,3 if (fail==1 and n==names[1]) or (fail==2 and n==names[2]) else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08005a74 if native else sym['case_boot_bus_open'])|1,0x20008000,count=1500)
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20003000,44)),bytes(u.mem_read(0x40002800,40)),trace))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_BOOT_BUS_OPEN',96)
