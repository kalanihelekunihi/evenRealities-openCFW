#!/usr/bin/env python3
"""Compare stock/source guarded frame call and guard-state behavior."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/guarded_frame_candidates.c';obj=HERE/'guarded_frame_candidates.o';elf=HERE/'guarded_frame_candidates.elf';ld=HERE/'guarded_frame_candidates.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
stubs={'case_legacy_ee_transport':0x0010f000,'case_legacy_pmic_transport':0x0010f100}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
entries={'case_legacy_ee_first':(0x080035d4,0x0800292c,'case_legacy_ee_transport'),'case_legacy_pmic_set':(0x080039e4,0x08002a00,'case_legacy_pmic_transport')}
for name,guard,selector in itertools.product(entries,[0,1,0xff],[0,1,16,20,0xff]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000029,bytes([guard]))
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[selector,0x20003000,1]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,address,size,user):
   target=entries[name][1] if original else stubs[entries[name][2]]
   if address!=target:return
   calls.append(tuple(uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]))
   uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((entries[name][0] if original else sym[name])|1,0x20001000,count=1000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,bytes(u.mem_read(0x20000029,1)),u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(name,guard,selector,pair)
print('PASS_GUARDED_FRAMES',30)
