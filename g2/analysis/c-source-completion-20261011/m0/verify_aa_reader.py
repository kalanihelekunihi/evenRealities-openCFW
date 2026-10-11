#!/usr/bin/env python3
"""Compare 0x9040 retry, fill, diagnostics, and logger at transaction cut."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/aa_reader_candidate.c';obj=HERE/'aa_reader_candidate.o';elf=HERE/'aa_reader_candidate.elf';ld=HERE/'aa_reader_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
stubs={'case_bus_input_transaction':0x0010f000,'case_legacy_logger':0x0010f100}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for count,success,flag in itertools.product([0,1,3],[0,1,5,10],[0,1]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x20003000,b'\xee'*8)
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[4,count,0x20003000]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];idx=[0]
  def hook(uc,address,size,user):
   if address in [0x080004c0,stubs['case_bus_input_transaction']]:
    calls.append(('read',*(uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3])))
    idx[0]+=1;val=1 if idx[0]==success else 0
   elif address in [0x08009170,stubs['case_legacy_logger']]:
    calls.append(('log',*(uc.reg_read(r) for r in [UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3])));val=0xaaaa
   else:return
   uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08009040 if original else sym['case_legacy_aa_read'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(0x20003000,8)),bytes(u.mem_read(0x20000080,4)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(count,success,flag,pair)
print('PASS_AA_READER',24)
