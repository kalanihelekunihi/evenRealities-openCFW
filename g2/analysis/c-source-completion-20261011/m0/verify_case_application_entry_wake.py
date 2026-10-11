#!/usr/bin/env python3
"""Compare stock/source app entry through 0x2fc8 after option and wake routes."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
subprocess.run(['/tmp/iar-c-runtime-venv/bin/python',str(HERE/'verify_case_application_entry_prefix.py')],check=True,capture_output=True)
elf=HERE/'application_entry_oracle.elf'
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
orig={0x08004eec:'clock',0x08008438:'input',0x08006a40:'pin',0x08002888:'power',0x08006bb0:'bus',0x08006c00:'sensor',0x080068f0:'console',0x08004a00:'options',0x08009170:'log',0x08004bf4:'prepare',0x08004b6c:'unlock',0x08004a6c:'write',0x08004b3c:'commit_a',0x08004b50:'commit_b',0x08004b20:'commit_c',0x08002fc8:'application'}
cand={sym['case_boot_'+n]&~1:n for n in ('clock_restore','input_initialize','pin_initialize','power_initialize','bus_initialize','sensor_initialize','console_initialize','read_option_words','log','option_prepare','option_unlock','option_write','option_commit_a','option_commit_b','option_commit_c')}
cand={k:({'clock_restore':'clock','input_initialize':'input','pin_initialize':'pin','power_initialize':'power','bus_initialize':'bus','sensor_initialize':'sensor','console_initialize':'console','read_option_words':'options','option_prepare':'prepare','option_unlock':'unlock','option_write':'write','option_commit_a':'commit_a','option_commit_b':'commit_b','option_commit_c':'commit_c'}.get(v,v)) for k,v in cand.items()};cand[sym['case_application_initialize_2fc8']&~1]='application'
checked=0
for fail,flag,silent in itertools.product((0,1),(0,0x8,0x20,0x28,0x100,0x108,0x120,0x128),(0,1)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_map(0x40007000,0x1000)
  u.mem_write(0x200000bf,bytes([silent]));u.mem_write(0x40007010,flag.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];lookup=orig if original else cand
  def hook(u,a,size,user):
   if a not in lookup:return
   name=lookup[a];calls.append(name)
   if name=='application':u.emu_stop();return
   if name=='options':
    vals=[7,0,0,0,0 if fail else 0xaa,0,0x1000000 if fail else 0]
    u.mem_write(u.reg_read(UC_ARM_REG_R0),b''.join(v.to_bytes(4,'little') for v in vals))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800a598 if original else sym['case_application_entry_a598'])|1,0x20001000,count=100000)
  assert calls and calls[-1]=='application',(original,fail,flag,silent,calls,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append((calls,bytes(u.mem_read(0x2000087c,1)),bytes(u.mem_read(0x40007018,4)),bytes(u.mem_read(0x4002103c,4))))
 assert pair[0]==pair[1],(fail,flag,silent,[(x[0],x[1].hex(),x[2].hex(),x[3].hex()) for x in pair])
 checked+=1
print('PASS_CASE_APPLICATION_ENTRY_WAKE',checked)
