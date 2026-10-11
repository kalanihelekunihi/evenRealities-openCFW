#!/usr/bin/env python3
"""Native-byte/C TLSF block size setter and split predicate."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/tlsf_split_block_candidate/split.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'split.o';e=t/'split.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 names=['g2_tlsf_block_size','g2_tlsf_block_to_ptr','g2_tlsf_align_ptr','g2_tlsf_block_mark_free','g2_file_close_error']
 args=['--defsym='+n+'='+hex(0x101011+i*0x10) for i,n in enumerate(names)]
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*args,'-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
 def run(native,entry,old,size):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  p=0x20008000;put(u,p+4,old);u.reg_write(A.UC_ARM_REG_R0,p);u.reg_write(A.UC_ARM_REG_R1,size);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  done=[False]
  def code(c,pc,_sz,_d):
   if pc==0x101180:done[0]=True;c.emu_stop()
   elif pc in (0x4cfd70 if native else 0x101010,):
    c.reg_write(A.UC_ARM_REG_R0,old&~3);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code)
  addr=(0x4cfd84 if entry=='set' else 0x4d01bc) if native else sym['g2_tlsf_block_set_size' if entry=='set' else 'g2_tlsf_block_can_split']
  u.emu_start(addr|1,0,count=100)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),word(u,p+4)
 n=0
 for entry in ('set','can'):
  for old in (0,1,2,3,12,15,28,31,100,0xffffffff):
   for size in (0,1,12,16,100,0xfffffff0,0xffffffff):
    a=run(True,entry,old,size);b=run(False,entry,old,size)
    assert a==b,(entry,old,size,a,b)
    n+=1
 print('PASS_AUDIO_TLSF_SPLIT_LEAVES',n)
