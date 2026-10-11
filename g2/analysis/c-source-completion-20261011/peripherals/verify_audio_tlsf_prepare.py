#!/usr/bin/env python3
"""Bounded native-byte/C TLSF allocation preparation child sequence."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/tlsf_prepare_allocation_candidate/prepare.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'prepare.o';e=t/'prepare.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 ext=['g2_tlsf_block_is_free','g2_tlsf_block_can_split','g2_tlsf_block_split','g2_tlsf_block_link_next','g2_tlsf_block_insert','g2_tlsf_block_next','g2_tlsf_block_to_ptr','g2_file_close_error']
 args=['--defsym='+name+'='+hex(0x101011+i*0x10) for i,name in enumerate(ext)]
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*args,'-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def string(u,a):return bytes(u.mem_read(a,100)).split(b'\0',1)[0].decode('ascii')
 def run(native,block,size):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.reg_write(A.UC_ARM_REG_R0,0x20001000);u.reg_write(A.UC_ARM_REG_R1,block);u.reg_write(A.UC_ARM_REG_R2,size);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  children=({0x4d039e:'trim',0x4cfeac:'mark',0x4cfe10:'ptr',0x4d09b4:'error'} if native else {sym['g2_tlsf_block_trim_free']&~1:'trim',sym['g2_tlsf_block_mark_used']&~1:'mark',0x101070:'ptr',0x101080:'error'})
  calls=[];done=[False]
  def code(c,pc,_sz,_data):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   kind=children.get(pc)
   if kind is None:return
   r=[c.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
   if kind=='error':args=(string(c,r[0]),string(c,r[1]),r[2])
   else:args=tuple(r[:3 if kind=='trim' else 1])
   calls.append((kind,args));c.reg_write(A.UC_ARM_REG_R0,0x20009000 if kind=='ptr' else 0);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x4d04e6 if native else sym['g2_tlsf_prepare_allocation'])|1,0,count=120)
  assert done[0],(native,block,size,hex(u.reg_read(A.UC_ARM_REG_PC)),calls,sym)
  return u.reg_read(A.UC_ARM_REG_R0),calls
 n=0
 for block in (0,0x20008000):
  for size in (0,4,12,1000):
   a=run(True,block,size);b=run(False,block,size)
   assert a==b,(block,size,a,b)
   n+=1
 print('PASS_AUDIO_TLSF_PREPARE',n)
