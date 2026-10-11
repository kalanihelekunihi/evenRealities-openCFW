#!/usr/bin/env python3
"""Historical stock-address startup oracle; default to current source gate.

Pass --legacy only to rerun the old isolated layout experiment. That layout
predates the typed CRT source and cannot link the current startup object alone.
"""
from pathlib import Path
import subprocess,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
if '--legacy' not in sys.argv:
 subprocess.run([sys.executable,str(HERE/'verify_case_startup_integrated.py')],check=True)
 print('CASE_STARTUP_LAYOUT_STOCK_ADDRESS_EXPERIMENT_SUPERSEDED')
 raise SystemExit(0)
obj=HERE/'startup_vector_candidate.o';elf=HERE/'startup_vector_candidate.elf'
sources=[ROOT/'g2/components/case/startup_candidate_20261011/startup_vector_candidate.c',
         ROOT/'g2/components/case/startup_candidate_20261011/startup_handler_forward_candidates.c']
parts=[]
for source in sources:
 part=HERE/(source.stem+'.test.o');parts.append(part)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os',
                 '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(part)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-r',*[str(part) for part in parts],'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(HERE/'case_startup_layout.ld'),str(obj),'-o',str(elf)],check=True,capture_output=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);table=e.get_section_by_name('.isr_vector').data()
 sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segments=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s.name.startswith('.text')]
source=[int.from_bytes(table[i:i+4],'little') for i in range(0,len(table),4)]
fixed=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
stock=[int.from_bytes(fixed[i:i+4],'little') for i in range(0,46*4,4)]
assert len(source)==len(stock)==46
default_slots=[i for i,x in enumerate(stock) if x==0x08000157]
for i,(before,after) in enumerate(zip(stock,source)):
 if i==1:assert after==(sym['case_reset_entry_0144']|1)
 elif i==2:assert after==(sym['case_vector_nmi_6d70']|1)
 elif i==3:assert after==(sym['case_vector_hardfault_6778']|1)
 elif i==11:assert after==(sym['case_vector_svc_6e18']|1)
 elif i in (18,28,38,43):
  name={18:'case_vector_irq_6e08',28:'case_vector_irq_06c4',38:'case_vector_irq_84b0',43:'case_vector_irq_8f98'}[i]
  assert after==(sym[name]|1)
 elif i in default_slots:assert after==(sym['case_vector_default_0156']|1)
 else:assert after==before,(i,hex(before),hex(after))
assert table[:4]==fixed[:4]
print('PASS_CASE_VECTOR_LAYOUT',len(source),'slots',len(default_slots),'default_handler_slots')
traces=[]
for original in (True,False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 u.mem_map(0x08000000,(len(fixed)+4095)&~4095);u.mem_write(0x08000000,fixed)
 for address,body in segments:u.mem_write(address,body)
 u.mem_map(0x20000000,0x10000);u.reg_write(UC_ARM_REG_SP,0x20008000)
 calls=[]
 def hook(uc,address,size,user):
  if address==(0x08000270 if original else (sym['case_crt_init_0270']&~1)):
   calls.append(('crt',uc.reg_read(UC_ARM_REG_SP)))
  elif address==0x0800a598:
   calls.append(('app',uc.reg_read(UC_ARM_REG_SP),uc.reg_read(UC_ARM_REG_R0)))
   uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((0x080000b8 if original else sym['case_startup_entry_00b8'])|1,0,count=100000)
 except Exception as exc:raise AssertionError((original,calls,hex(u.reg_read(UC_ARM_REG_PC)),str(exc))) from exc
 traces.append((calls,bytes(u.mem_read(0x20000000,0x2c88))))
if traces[0]!=traces[1]:
 import hashlib
 raise AssertionError((traces[0][0],traces[1][0],hashlib.sha256(traces[0][1]).hexdigest(),hashlib.sha256(traces[1][1]).hexdigest()))
print('PASS_CASE_STARTUP_ENTRY',len(traces[0][0]),'boundary_calls',len(traces[0][1]),'ram_bytes')
forward=[('case_vector_irq_06c4',0x080006c4,0x08004330,0x200008e4),
         ('case_vector_irq_6e08',0x08006e08,0x08005a52,0x20000948),
         ('case_vector_irq_84b0',0x080084b0,0x08005c90,0x20000f4c),
         ('case_vector_irq_8f98',0x08008f98,0x08005f50,0x20000e24)]
for name,stock_entry,lower,argument in forward:
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(fixed)+4095)&~4095);u.mem_write(0x08000000,fixed)
  for address,body in segments:u.mem_write(address,body)
  u.mem_map(0x20000000,0x10000)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   if address==lower:
    calls.append((address,uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((stock_entry if original else sym[name])|1,0x20001000,count=1000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append(calls)
 assert pair[0]==pair[1]==[(lower,argument)],(name,pair)
print('PASS_CASE_VECTOR_FORWARD',len(forward),'handlers')
