#!/usr/bin/env python3
"""Compare stock/source control report loops at read/logger/hex cuts."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/control_dump_candidates.c';obj=HERE/'control_dump_candidates.o';elf=HERE/'control_dump_candidates.elf';ld=HERE/'control_dump_candidates.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_legacy_logger','case_legacy_aa_read','case_legacy_ee_first','case_binary_5e_hex']
stock=[0x08009170,0x08009040,0x080035d4,0x080067c8]
stubs={n:0x0010f000+0x100*i for i,n in enumerate(names)}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
entries={'case_legacy_aa_first':0x0800d1bc,'case_legacy_aa_second':0x0800d218,'case_legacy_ab_child':0x08003558}
def cstr(u,p):
 out=bytearray()
 for i in range(100):
  b=u.mem_read(p+i,1)[0]
  if not b:return out.decode()
  out.append(b)
 raise AssertionError('no nul')
for name,flag,byte in itertools.product(entries,[0,1],[0,0x71]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x20000090,bytes(range(8)))
  u.reg_write(UC_ARM_REG_R0,0x12345678);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   try:i=(stock if original else list(stubs.values())).index(address&~1)
   except ValueError:return
   if i==0:
    fmt=cstr(uc,uc.reg_read(UC_ARM_REG_R0));arg=uc.reg_read(UC_ARM_REG_R1) if '%' in fmt else None
    calls.append(('log',fmt,arg))
   elif i==1:
    off=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);out=uc.reg_read(UC_ARM_REG_R2)
    calls.append(('read',off,n));uc.mem_write(out,bytes([byte]))
   elif i==2:
    sel=uc.reg_read(UC_ARM_REG_R0);out=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2)
    calls.append(('ee',sel,n));uc.mem_write(out,bytes([byte]))
   else:calls.append(('hex',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   uc.reg_write(UC_ARM_REG_R0,0x76543210);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((entries[name] if original else sym[name])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(name,flag,byte,pair)
print('PASS_CONTROL_DUMPS',12)
