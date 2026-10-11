#!/usr/bin/env python3
"""Bounded stock/source oracle for chunked LittleFS block CRC."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/bd_crc.c';O=D/'bd-crc-m4.o';E=D/'bd-crc-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_bd_read=0x101001','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,size,error):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 sp=0x200f0000;out=0x20001000;w(out,0xffffffff)
 for i,v in enumerate((3,0,size,out)):w(sp+4*i,v)
 for reg,v in ((A.UC_ARM_REG_R0,0x20002000),(A.UC_ARM_REG_R1,0),(A.UC_ARM_REG_R2,0x20002000),(A.UC_ARM_REG_R3,16),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4ca83c if stock else 0x101000):
   s=cpu.reg_read(A.UC_ARM_REG_SP);off=rd(s+4);n=rd(s+12);events.append(('read',off,n))
   if not error:cpu.mem_write(rd(s+8),bytes(((off+i)&0xff for i in range(n))))
   result=error
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4caa88 if stock else sy['g2_lfs_bd_crc'])|1,0,count=500)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),events,rd(out)
n=0
for size in (0,1,7,8,9,15,24):
 for error in (0,-5,-84):
  a=run(True,size,error);b=run(False,size,error)
  assert a==b,(size,error,a,b);n+=1
print('PASS_BD_CRC',n)
