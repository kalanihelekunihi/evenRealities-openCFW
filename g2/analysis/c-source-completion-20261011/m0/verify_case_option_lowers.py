#!/usr/bin/env python3
"""Bounded native/source option-register operation comparison."""
from pathlib import Path
import subprocess,random,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/application_boot_lowers_candidate.c'
obj=HERE/'application_boot_lowers_oracle.o';elf=HERE/'application_boot_lowers_oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
entries={'case_boot_option_prepare':0x08004bf4,'case_boot_option_unlock':0x08004b6c,'case_boot_option_commit_a':0x08004b3c,'case_boot_option_commit_b':0x08004b50,'case_boot_option_commit_c':0x08004b20}
checked=0
for name,status,seed in itertools.product(entries,(0,0x40000000,0x80000000,0xc0000000),range(4)):
 raw=bytearray(random.Random(seed).randbytes(0x80));raw[20:24]=status.to_bytes(4,'little');pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40022000,0x1000);u.mem_write(0x40022000,bytes(raw))
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((entries[name] if original else sym[name])|1,0x20001000,count=5000)
  pair.append((u.reg_read(UC_ARM_REG_PC),bytes(u.mem_read(0x40022000,0x80))))
 assert pair[0]==pair[1],(name,hex(status),seed)
 checked+=1
print('PASS_CASE_OPTION_LOWERS',checked)
