#!/usr/bin/env python3
"""Native/source CASE 0x4a6c option writer at flash wait child cuts."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];S=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for name in ['application_boot_option_read_candidate','application_boot_option_write_candidate']:
 obj=H/(name+'.oracle.o');subprocess.run(flags+[str(S/(name+'.c')),'-o',str(obj)],check=True);objs.append(str(obj))
stub=H/'boot_option_write.oracle_stub.c';stubobj=H/'boot_option_write.oracle_stub.o';elf=H/'boot_option_write.oracle.elf'
stub.write_text('#include <stdint.h>\nuint32_t case_boot_option_wait(uint32_t ticks){return ticks;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*objs,str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x4a6c)
for i in range(96):
 words=[rng.choice([0,1,2,3,4,6,7,8]),rng.choice([0,1,4,8]),rng.getrandbits(7),rng.getrandbits(7),rng.getrandbits(32),rng.getrandbits(32),rng.getrandbits(32)]
 busy=i%17==0;wait_result=i%3;initial=rng.getrandbits(32);pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40022000,0x1000)
  u.mem_write(0x20003000,struct.pack('<7I',*words));u.mem_write(0x20000f98,bytes([int(busy)]));u.mem_write(0x40022020,struct.pack('<I',initial))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  cut=0x08003f6c if native else sym['case_boot_option_wait']&~1;trace=[]
  def hook(uc,a,size,_):
   if a==cut:trace.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,wait_result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08004a6c if native else sym['case_boot_option_write'])|1,0x20008000,count=1000)
  mmio=tuple(bytes(u.mem_read(a,4)) for a in [0x40022014,0x40022020,0x4002202c,0x40022030,0x4002204c,0x40022050])
  pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000f98,8)),mmio,trace))
 assert pair[0]==pair[1],(i,words,pair)
print('PASS_CASE_BOOT_OPTION_WRITE',96)
