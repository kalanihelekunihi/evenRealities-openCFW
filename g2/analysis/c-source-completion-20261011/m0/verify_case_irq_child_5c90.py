#!/usr/bin/env python3
"""CASE 0x5c90 original/C timer IRQ state and MMIO oracle."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3];F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_irq_child_5c90_candidate.c';obj=H/'irq_child_5c90.oracle.o';elf=H/'irq_child_5c90.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x5c90);masks=[0,1,2,4,8,16,32,64,128,256,0x1ff]
for i in range(256):
 base=0x40014800 if i%2 else 0x40014400
 state=bytearray(rng.randbytes(0x40));state[:4]=struct.pack('<I',base)
 device=bytearray(rng.randbytes(0x40));enable=masks[i%len(masks)];status=masks[(i//3)%len(masks)]
 device[12:16]=struct.pack('<I',enable);device[16:20]=struct.pack('<I',status)
 accum=bytearray(rng.randbytes(16));pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40014000,0x1000)
  u.mem_write(0x20003000,bytes(state));u.mem_write(0x20000118,bytes(accum));u.mem_write(base,bytes(device))
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20003000)
  u.emu_start((0x08005c90 if native else sym['case_irq_child_5c90'])|1,0x20008000,count=1600)
  pair.append((bytes(u.mem_read(0x20003000,0x40)),bytes(u.mem_read(0x20000118,16)),bytes(u.mem_read(base,0x40))))
 assert pair[0]==pair[1],(i,hex(base),hex(enable),hex(status),[(k,[(j,a,b) for j,(a,b) in enumerate(zip(pair[0][k],pair[1][k])) if a!=b][:8]) for k in range(3)])
print('PASS_CASE_IRQ_CHILD_5C90',256)
