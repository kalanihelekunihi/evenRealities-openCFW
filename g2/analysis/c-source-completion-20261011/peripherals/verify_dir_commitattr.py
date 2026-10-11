#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS commitprog and commitattr."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_commitattr.c';O=D/'dir-commitattr-m4.o';E=D/'dir-commitattr-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_bd_program=0x101001','--defsym=g2_lfs_bd_read=0x101011','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,tag,limit,program_err,read_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20001000;commit=0x20002000;buf=0x20003000;sp=0x200f0000
 for i,v in enumerate((7,4,0xffffffff,0xffffffff,0,limit)):w(commit+4*i,v)
 if tag&0x80000000:w(buf,9);w(buf+4,16)
 else:u.mem_write(buf,b'abcdefgh')
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,commit),(A.UC_ARM_REG_R2,tag),(A.UC_ARM_REG_R3,buf),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cac04 if stock else 0x101000):
   s=cpu.reg_read(A.UC_ARM_REG_SP);ptr=rd(s+8);n=rd(s+12)
   events.append(('prog',rd(s),rd(s+4),bytes(cpu.mem_read(ptr,n))))
   result=program_err
  elif pc==(0x4ca83c if stock else 0x101010):
   s=cpu.reg_read(A.UC_ARM_REG_SP);events.append(('read',rd(s),rd(s+4),rd(s+12)))
   if not read_err:cpu.mem_write(rd(s+8),b'Z')
   result=read_err
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cc23c if stock else sy['g2_lfs_dir_commitattr'])|1,0,count=2000)
 assert done[0],(stock,events)
 return u.reg_read(A.UC_ARM_REG_R0),events,bytes(u.mem_read(commit,24))
n=0
for tag in (0x20200008,0xa0200008,0x4ff00000):
 for limit in (4,8,100):
  for pe in (0,-5):
   for re in (0,-84):
    a=run(True,tag,limit,pe,re);b=run(False,tag,limit,pe,re)
    assert a==b,(hex(tag),limit,pe,re,a,b);n+=1
print('PASS_DIR_COMMITATTR',n)
