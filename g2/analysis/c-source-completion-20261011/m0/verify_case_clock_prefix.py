#!/usr/bin/env python3
"""Stock/source 0x4f14 compare through descriptor-prepare entry only."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/clock_plan_candidate.c'
stub=HERE/'clock_prefix_oracle_stubs.c';stub.write_text('#include <stdint.h>\n')
objs=[]
for source in (SRC,stub):
 obj=HERE/(source.stem+'.oracle.o');objs.append(obj)
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-fno-inline','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(source),'-o',str(obj)],check=True)
elf=HERE/'clock_prefix_oracle.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-e','case_transfer_clock_config','-Ttext=0x00100000',*[str(x) for x in objs],'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
assert 'descriptor_prepare' in sym
checked=0
for plan,rate,prescale in itertools.product((0,1,3,4),(0xf4240,0x3d0900),(0,0x1000)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_map(0x40022000,0x1000);u.mem_map(0x40014000,0x1000)
  u.mem_write(0x20000124,rate.to_bytes(4,'little'));u.mem_write(0x40021008,prescale.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,plan);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  target=0x08005bda if original else sym['descriptor_prepare']&~1
  seen=[]
  def cut(u,a,size,user):
   if a==target:seen.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000f4c,0x20)),bytes(u.mem_read(0x40021040,4))));u.emu_stop()
  u.hook_add(UC_HOOK_CODE,cut)
  u.emu_start((0x08004f14 if original else sym['case_transfer_clock_config'])|1,0x20001000,count=5000)
  assert len(seen)==1,(original,plan,rate,prescale,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append(seen[0])
 assert pair[0][1:]==pair[1][1:],(plan,rate,prescale,[(x[0],x[1].hex(),x[2].hex()) for x in pair])
 checked+=1
print('PASS_CASE_CLOCK_PREFIX',checked)
