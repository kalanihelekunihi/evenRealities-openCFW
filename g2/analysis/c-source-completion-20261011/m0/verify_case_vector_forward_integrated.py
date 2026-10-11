#!/usr/bin/env python3
"""Compare four CASE vector forwarding cuts at the clean source ELF layout."""
from pathlib import Path
import subprocess,sys,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
forward=[('case_vector_irq_06c4',0x080006c4,'case_irq_child_4330',0x08004330,0x200008e4),
 ('case_vector_irq_6e08',0x08006e08,'case_irq_child_5a52',0x08005a52,0x20000948),
 ('case_vector_irq_84b0',0x080084b0,'case_irq_child_5c90',0x08005c90,0x20000f4c),
 ('case_vector_irq_8f98',0x08008f98,'case_irq_child_5f50',0x08005f50,0x20000e24)]
with tempfile.TemporaryDirectory() as d:
 elf=Path(d)/'source.elf'
 subprocess.run([sys.executable,str(H/'build_case_absolute_experiment.py'),'--output',str(elf)],check=True,capture_output=True)
 with elf.open('rb') as f:
  e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
  segments=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 for src,stock_entry,child,stock_child,expected in forward:
  results=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
   if native:
    u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
   else:
    u.mem_map(0x08000000,0x20000)
    for addr,data in segments:u.mem_write(addr,data)
   u.mem_map(0x20000000,0x10000)
   u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20001001)
   observed=[];target=stock_child if native else syms[child]&~1
   def hook(uc,address,size,_):
    if address==target:
     observed.append((address,uc.reg_read(UC_ARM_REG_R0)))
     uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((stock_entry if native else syms[src])|1,0,count=200)
   assert len(observed)==1,(src,native,observed,hex(u.reg_read(UC_ARM_REG_PC)))
   results.append(observed[0][1])
  assert results==[expected,expected],(src,results,hex(expected))
 print('PASS_CASE_VECTOR_FORWARD_INTEGRATED',len(forward))
