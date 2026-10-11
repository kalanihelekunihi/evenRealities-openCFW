#!/usr/bin/env python3
"""Bounded stock/C error recovery comparison for native CASE 86f4."""
from pathlib import Path
import random,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_boot_sensor_irq_error_candidate.c';obj=H/'sensor_irq_error.oracle.o';elf=H/'sensor_irq_error.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x86f4)
for i in range(128):
 p=bytearray(rng.randbytes(0xa0));hw=bytearray(rng.randbytes(0x40));struct.pack_into('<I',p,0,0x40010000);struct.pack_into('<I',p,108,i%3==0)
 pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F);u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40010000,0x1000);u.mem_write(0x20002000,bytes(p));u.mem_write(0x40010000,bytes(hw))
  u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
  u.emu_start((0x080086f4 if native else sym['case_boot_sensor_irq_error'])|1,0x20008000,count=300)
  pair.append((bytes(u.mem_read(0x20002000,0xa0)),bytes(u.mem_read(0x40010000,0x40)),u.reg_read(UC_ARM_REG_PRIMASK)))
 assert pair[0]==pair[1],(i,[(hex(j),a,b) for j,(a,b) in enumerate(zip(pair[0][0]+pair[0][1],pair[1][0]+pair[1][1])) if a!=b][:8])
print('PASS_CASE_SENSOR_IRQ_ERROR',128)
