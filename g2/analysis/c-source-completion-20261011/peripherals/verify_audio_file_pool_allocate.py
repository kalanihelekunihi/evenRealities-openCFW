#!/usr/bin/env python3
"""Original-byte/C ordered TLSF pool allocation child-call comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/file_pool_allocate_candidate/pool_allocate.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'pool.o';e=t/'pool.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subs=['--defsym=g2_tlsf_adjust_request=0x101011','--defsym=g2_tlsf_find_suitable=0x101021','--defsym=g2_tlsf_prepare_allocation=0x101031']
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*subs,'-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,size,adjusted,block):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.reg_write(A.UC_ARM_REG_R0,0x20008800);u.reg_write(A.UC_ARM_REG_R1,size);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  children=({0x4cff42:('adjust',adjusted),0x4d0484:('find',block),0x4d04e6:('prepare',0x20009000)} if native else {0x101010:('adjust',adjusted),0x101020:('find',block),0x101030:('prepare',0x20009000)})
  calls=[];done=[False]
  def code(c,pc,_size,_data):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   if pc not in children:return
   kind,result=children[pc]
   calls.append((kind,tuple(c.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))[:2 if kind!='prepare' else 3]))
   c.reg_write(A.UC_ARM_REG_R0,result);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x4d0722 if native else sym['g2_file_pool_allocate'])|1,0,count=100)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),calls
 n=0
 for size in (0,1,4,16,1000,0xffffffff):
  for adjusted in (0,4,16,1000):
   for block in (0,0x20008100):
    a=run(True,size,adjusted,block);b=run(False,size,adjusted,block)
    assert a==b,(size,adjusted,block,a,b)
    n+=1
 print('PASS_AUDIO_FILE_POOL_ALLOCATE',n)
