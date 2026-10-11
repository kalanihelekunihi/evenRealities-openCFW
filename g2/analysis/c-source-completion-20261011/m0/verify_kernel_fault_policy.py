#!/usr/bin/env python3
"""Authenticate the exact native CPSID/self-branch fault policy."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/kernel_fault_policy_candidate.c'
obj=HERE/'kernel_fault_policy_candidate.o'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
with obj.open('rb') as stream:
 e=ELFFile(stream);body=e.get_section_by_name('.text').data()
 symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
expected=bytes.fromhex('72 b6 fe e7')
source_addrs=[symbols['case_kernel_invariant_failure']&~1,symbols['case_kernel_nesting_underflow']&~1]
stock_addrs=[0x0800c028,0x0800c7be,0x0800c7c8,0x0800c7d6,0x0800c69c,0x0800c6a6,0x0800c6b4,0x0800c6c6,0x0800cb4a,0x0800cb66]
for address in source_addrs:assert body[address:address+4]==expected
for address in stock_addrs:assert FW[address-0x08000000:address-0x08000000+4]==expected
for address in source_addrs+stock_addrs:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 execution=0x00100000;u.mem_map(execution,0x1000)
 u.mem_write(execution,expected)
 u.reg_write(UC_ARM_REG_PRIMASK,0)
 u.emu_start(execution|1,0,count=8)
 assert u.reg_read(UC_ARM_REG_PRIMASK)==1
 assert u.reg_read(UC_ARM_REG_PC)==execution+2
print('PASS_KERNEL_NATIVE_FAULT_POLICY',len(source_addrs),len(stock_addrs))
