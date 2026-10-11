#!/usr/bin/env python3
"""Full 0x0800373c stock/source control-flow oracle at typed flash lowers."""
from pathlib import Path
import itertools,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/legacy_default_candidate_20261010/flash_apply_candidate.c'
obj=HERE/'flash_apply_candidate.o';elf=HERE/'flash_apply_candidate.elf';ld=HERE/'flash_apply_candidate.ld'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
names=['case_binary_5e_flash_mode','case_binary_5e_flash_init','case_binary_5e_flash_read',
       'case_binary_5e_wait','case_binary_5e_flash_program','case_binary_5e_flash_finish','case_binary_5e_failure_log']
source_addrs={0x0010f000+0x100*i:n for i,n in enumerate(names)}
stock_addrs=dict(zip([0x08002f46,0x08004bf4,0x0800497c,0x08004958,0x08004b94,0x08004b20,0x08009170],names))
ld.write_text(''.join(f'{name} = 0x{address|1:08x};\n' for address,name in source_addrs.items())+
              'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def cstr(u,p):
 out=bytearray()
 for i in range(100):
  b=u.mem_read(p+i,1)[0]
  if not b:return out.decode()
  out.append(b)
 raise AssertionError('unterminated')
rows=[]
for erase,program,mode,flag,pattern in itertools.product(
        [(0,), (1,0), (1,1,0), (1,1,1)], [(0,0),(1,),(0,1)], [1,2], [0,1], [bytes(range(16)),bytes(reversed(range(16))) ]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20004000,pattern);u.mem_write(0x200000bf,bytes([flag]))
  u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R3,0xdeadbeef)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[];reads=[0];programs=[0]
  def hook(uc,address,size,user):
   name=(stock_addrs if original else source_addrs).get(address)
   if not name:return
   if name=='case_binary_5e_flash_mode':
    events.append(('mode',));value=mode
   elif name=='case_binary_5e_flash_init':
    events.append(('init',));value=0x4321
   elif name=='case_binary_5e_flash_read':
    assert uc.reg_read(UC_ARM_REG_R0)==0x200001a4
    events.append(('read',bytes(uc.mem_read(0x200001a4,16)).hex()))
    uc.mem_write(uc.reg_read(UC_ARM_REG_R1),struct.pack('<I',0x1234+reads[0]))
    value=erase[reads[0]];reads[0]+=1
   elif name=='case_binary_5e_wait':
    events.append(('wait',uc.reg_read(UC_ARM_REG_R0)));value=0x4321
   elif name=='case_binary_5e_flash_program':
    events.append(('program',*(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))))
    value=program[programs[0]];programs[0]+=1
   elif name=='case_binary_5e_flash_finish':
    events.append(('finish',));value=0x4321
   else:
    fmt=cstr(uc,uc.reg_read(UC_ARM_REG_R0))
    events.append(('log',fmt,uc.reg_read(UC_ARM_REG_R1) if '%x' in fmt else None));value=0x4321
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x0800373c if original else sym['case_binary_5e_apply'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append((events,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200001a4,16)).hex()))
 assert pair[0]==pair[1],(erase,program,mode,flag,pattern.hex(),pair)
 rows.append((erase,program,mode,flag,pattern.hex()))
print('PASS_FULL_FLASH_APPLY_TYPED_LOWERS',len(rows))
