#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS parent search dispatch."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/fs_parent.c';O=D/'fs-parent-m4.o';E=D/'fs-parent-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_tortoise_detectcycles=0x101001','--defsym=g2_lfs_dir_fetchmatch=0x101011','--defsym=g2_lfs_bd_read=0x101021','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,cycle,fetch):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 pair=0x20001000;out=0x20002000;w(pair,3);w(pair+4,4);u.mem_write(out,b'X'*32)
 for reg,v in ((A.UC_ARM_REG_R0,0x20003000),(A.UC_ARM_REG_R1,pair),(A.UC_ARM_REG_R2,out),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cef18 if stock else 0x101000):
   p=cpu.reg_read(A.UC_ARM_REG_R0);events.append(('cycle',rd(p+24),rd(p+28)));result=cycle
  elif pc==(0x4cb968 if stock else 0x101010):
   p=cpu.reg_read(A.UC_ARM_REG_R1)
   events.append(('match',rd(p+24),rd(p+28),cpu.reg_read(A.UC_ARM_REG_R3)))
   if fetch in (0,-2):w(p+24,0xffffffff);w(p+28,0xffffffff)
   result=fetch
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cf4da if stock else sy['g2_lfs_fs_parent'])|1,0,count=500)
 assert done[0],(stock,events)
 return u.reg_read(A.UC_ARM_REG_R0),events,bytes(u.mem_read(out+24,8))
n=0
for cycle in (0,-84):
 for fetch in (-84,-2,0,0x20000008):
  a=run(True,cycle,fetch);b=run(False,cycle,fetch)
  assert a==b,(cycle,fetch,a,b);n+=1
print('PASS_FS_PARENT',n)
