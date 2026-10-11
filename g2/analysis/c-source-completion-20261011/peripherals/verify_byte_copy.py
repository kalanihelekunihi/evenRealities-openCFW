#!/usr/bin/env python3
"""Original/source ARM copy memory and return oracle."""
from pathlib import Path
import subprocess,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
O=D/'byte-copy-m4.o';E=D/'byte-copy-m4.elf';S=R/'g2/components/audio/file_sync_candidate/byte_copy.c'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,n,src_align,dst_align):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,s in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,s)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 source=0x20011000+src_align;dest=0x20012000+dst_align
 u.mem_write(source,bytes((x*17+3)&255 for x in range(128)))
 u.mem_write(dest,b'\x91'*128)
 for reg,v in ((A.UC_ARM_REG_R0,dest),(A.UC_ARM_REG_R1,source),
               (A.UC_ARM_REG_R2,n),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x439be4 if stock else sy['g2_lfs_memcpy'])|1,0,count=1000)
 assert done[0]
 return bytes(u.mem_read(dest,128))
count=0
for sa in range(4):
 for da in range(4):
  for n in (0,1,2,3,4,5,7,8,15,16,17,31,32,63,64,95):
   a=run(True,n,sa,da);b=run(False,n,sa,da)
   assert a==b,(n,sa,da)
   count+=1
print('PASS_BYTE_COPY',count)
