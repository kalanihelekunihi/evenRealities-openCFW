#!/usr/bin/env python3
"""Stock/source program-wrapper comparison at status and physical leaf cuts."""
from pathlib import Path
import itertools,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/flash_operations_candidate.c'
obj=HERE/'flash_operations_candidate.o';elf=HERE/'flash_operations_candidate.elf';ld=HERE/'flash_operations_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
stubs={'case_tick_word2':0x0010f000,'case_flash_erase_mode4':0x0010f100,'case_flash_erase_page':0x0010f200,
       'case_flash_program_doubleword':0x0010f300,'case_flash_copy_operation':0x0010f400}
ld.write_text(''.join(f'{k} = 0x{v|1:08x};\n' for k,v in stubs.items())+
              'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
rows=[]
for operation,statuses,locked in itertools.product([1,2,0xffffffff],[(0,0),(0,3),(1,)], [0,1]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40022000,0x1000)
  u.mem_write(0x20000f98,bytes([locked]));u.mem_write(0x40022014,(0xffffffff).to_bytes(4,'little'))
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],
                     [operation,0x0803f000,0x12345678,0x9abcdef0]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];status_index=[0];writes=[]
  def hook(uc,address,size,user):
   if address in [0x08003f6c,sym['case_flash_status_wait']&~1]:
    assert uc.reg_read(UC_ARM_REG_R0)==1000
    calls.append(('status',1000));value=statuses[status_index[0]];status_index[0]+=1
   elif address in [0x08003f1c,stubs['case_flash_program_doubleword']]:
    calls.append(('double',*(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))));value=0x7777
   elif address in [0x08003f38,stubs['case_flash_copy_operation']]:
    calls.append(('copy',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));value=0x7777
   else:return
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def write(uc,access,address,size,value,user):
   if address in [0x20000f98,0x20000f9c,0x40022014]:writes.append((address,size,value))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x08004b94 if original else sym['case_binary_5e_flash_program'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((calls,writes,u.reg_read(UC_ARM_REG_R0)))
 assert pair[0]==pair[1],(operation,statuses,locked,pair)
 rows.append((operation,statuses,locked))
print('PASS_FLASH_PROGRAM_WRAPPER',len(rows))
