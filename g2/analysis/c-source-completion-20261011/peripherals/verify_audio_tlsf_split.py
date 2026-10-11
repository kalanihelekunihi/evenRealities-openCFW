#!/usr/bin/env python3
"""Native-byte/C TLSF block-split memory and child comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];AUDIO=R/'g2/components/audio';S=AUDIO/'tlsf_split_block_candidate/split.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);f=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror'];objs=[]
 for i,source in enumerate((S,AUDIO/'file_pool_free_candidate/tlsf_align.c',AUDIO/'file_pool_free_candidate/tlsf_absorb_leaves.c')):
  o=t/f'{i}.o';subprocess.run(f+['-c',str(source),'-o',str(o)],check=True);objs.append(o)
 e=t/'split.elf';args=['--defsym=g2_tlsf_block_mark_free=0x101011','--defsym=g2_tlsf_block_next=0x101021','--defsym=g2_file_close_error=0x101031']
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*args,'-o',str(e),*[str(o) for o in objs]],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as ef:
  elf=ELFFile(ef);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def string(u,a):return bytes(u.mem_read(a,110)).split(b'\0',1)[0].decode('ascii')
 def run(native,old,split,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  block=0x20008000;put(u,block+4,old|flags)
  u.reg_write(A.UC_ARM_REG_R0,block);u.reg_write(A.UC_ARM_REG_R1,split);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  calls=[];done=[False];mark=0x4cfe96 if native else 0x101010;error=0x4d09b4 if native else 0x101030
  def code(c,pc,_sz,_d):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   if pc==mark:calls.append(('mark',c.reg_read(A.UC_ARM_REG_R0)));c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
   elif pc==error:
    r=[c.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
    calls.append(('error',string(c,r[0]),string(c,r[1]),r[2]));c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x4d01d4 if native else sym['g2_tlsf_block_split'])|1,0,count=1000)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(block,128)),calls
 n=0
 for old in (32,48,64,100,256):
  for split in (4,8,12,16,20,32):
   if old<split+16:continue
   for flags in (0,1,2,3):
    a=run(True,old,split,flags);b=run(False,old,split,flags)
    assert a==b,(old,split,flags,a,b)
    n+=1
 print('PASS_AUDIO_TLSF_SPLIT',n)
