"""Whole CASE binary entry 06/41 handoff to the legacy handler."""
from pathlib import Path
import itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
E=Path(__file__).with_name('case-binary-whole.elf')
with E.open('rb') as f:
 elf=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in elf.iter_segments() if x['p_type']=='PT_LOAD'];syms={x.name:x['st_value'] for x in elf.get_section_by_name('.symtab').iter_symbols()}
for op,n,flag,ack_return in itertools.product((6,0x41),(0,1,4,20),(0,1,0x7f),(0,0x12345678)):
 results=[]
 for is_c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,B);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_write(0x20004000,bytes([op,0,2,0,0])+bytes(251));u.mem_write(0x200000bf,bytes([flag]))
  events=[]
  ack=(syms['case_binary_ack0641']&~1) if is_c else 0x080068d0
  legacy=(syms['case_legacy_command_candidate']&~1) if is_c else 0x08000928
  def hook(uc,a,size,_):
   if a==ack:events.append(('ack',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,ack_return);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a==legacy:
    p=uc.reg_read(UC_ARM_REG_R0);events.append(('legacy',uc.mem_read(p,1)[0],uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_R0,0x11223344);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_R2,0)
  u.emu_start((syms['case_binary_command_candidate'] if is_c else 0x08000e1c)|1,0x20001000,count=10000)
  results.append((u.reg_read(UC_ARM_REG_R0),events))
 assert results[0]==results[1],(op,n,flag,ack_return,results)
 print('PASS',op,n,flag,ack_return,results[0])
