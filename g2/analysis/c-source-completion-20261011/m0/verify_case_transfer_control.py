#!/usr/bin/env python3
"""Bounded native/source comparison for peripheral control 0x08005528."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/transfer_control_candidate.c'
obj=HERE/'transfer_control_candidate.oracle.o';elf=HERE/'transfer_control_candidate.oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(SRC),'-o',str(obj)],check=True)
stub=HERE/'transfer_control_oracle_stubs.c';stub.write_text('#include <stdint.h>\nuint32_t case_tick_word2(void){return *(volatile uint32_t *)(uintptr_t)0x20000120u;}\nuint32_t case_transfer_clock_config(uint32_t p){return p;}\n')
stubobj=HERE/'transfer_control_oracle_stubs.o';subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-c',str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-e','case_transfer_control_5528','--unresolved-symbols=ignore-all','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for flags,check,mode_bits in itertools.product((0,1,2,4,8),(0,1),(0,0x10,0x20)):
 if flags==2 and mode_bits==0:continue
 cfg=bytearray(0x40);cfg[0]=flags;cfg[28:32]=check.to_bytes(4,'little')
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20007000,bytes(cfg))
  u.mem_map(0x40021000,0x1000);u.mem_map(0x40007000,0x1000)
  u.mem_write(0x40021008,mode_bits.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,0x20007000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  try:u.emu_start((0x08005528 if original else sym['case_transfer_control_5528'])|1,0x20001000,count=20000)
  except Exception as e:raise AssertionError((original,flags,check,mode_bits,hex(u.reg_read(UC_ARM_REG_PC)),str(e)))
  out=(u.reg_read(UC_ARM_REG_PC),u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x40021000,0x80)),bytes(u.mem_read(0x40007000,0x10)))
  if original:baseline=out
  else:
   assert baseline==out,(flags,check,mode_bits,baseline[:2],out[:2],[(i,a,b) for i,(a,b) in enumerate(zip(baseline[2],out[2])) if a!=b][:10])
 checked+=1
print('PASS_CASE_TRANSFER_CONTROL_BOUNDED',checked)
