#!/usr/bin/env python3
"""Whole task initializer RAM comparison with symbolic return-handler pointer."""
from pathlib import Path
import random,subprocess,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];folder=R/'g2/components/case/startup_candidate_20261011'
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
objs=[]
for base in ('application_boot_task_frame_candidate','application_boot_task_initialize_candidate'):
 obj=H/(base+'.oracle.o');subprocess.run(flags+[str(folder/(base+'.c')),'-o',str(obj)],check=True);objs.append(obj)
elf=H/'application_boot_task_frame.oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',*[str(x) for x in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0xae96)
for i in range(96):
 storage=0x200015d0;stack_end=0x2000162c;words=[0x80,0x100,0x20][i%3];priority=i%64
 seed=bytes(rng.randrange(256) for _ in range(0x600));pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(storage,seed);u.mem_write(storage+0x30,struct.pack('<I',stack_end))
  sp=0x20007fc0;u.mem_write(sp,struct.pack('<IIII',priority,0x20003000,storage,0))
  u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.reg_write(UC_ARM_REG_R0,0x0800ae5d);u.reg_write(UC_ARM_REG_R1,0x0800c2e8 if i&1 else 0)
  u.reg_write(UC_ARM_REG_R2,words);u.reg_write(UC_ARM_REG_R3,0x20004000)
  u.emu_start((0x0800ae96 if native else sym['case_boot_task_initialize'])|1,0x20001000,count=5000)
  data=bytearray(u.mem_read(storage,0x600));top=struct.unpack_from('<I',data,0)[0]
  # LR slot embeds an address in two distinct code layouts.
  struct.pack_into('<I',data,top+52-storage,0x0800b31d)
  pair.append((bytes(data),bytes(u.mem_read(0x20003000,4))))
 assert pair[0]==pair[1],(i,[(p[0][:0x60].hex(),p[1].hex()) for p in pair])
print('PASS_CASE_BOOT_TASK_FRAME',96)
