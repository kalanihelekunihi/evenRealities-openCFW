#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS metadata attribute traversal."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_traverse.c';O=D/'dir-traverse-m4.o';E=D/'dir-traverse-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_bd_read=0x101001','--defsym=g2_file_close_error=0x101011','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,tags,mask,wanted,cb_result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 sp=0x200f0000;dir=0x20002000;attrs=0x20003000;buf=0x20004000
 u.mem_write(dir,b'\0'*32);u.mem_write(buf,b'abcd')
 for i,tag in enumerate(tags):w(attrs+i*8,tag);w(attrs+i*8+4,buf)
 for i,v in enumerate((attrs,len(tags),mask,wanted,0,0x3ff,0,0x101031,0x20005000)):w(sp+i*4,v)
 for reg,v in ((A.UC_ARM_REG_R0,0x20001000),(A.UC_ARM_REG_R1,dir),(A.UC_ARM_REG_R2,0),(A.UC_ARM_REG_R3,0xffffffff),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==0x101030:
   events.append(('visit',cpu.reg_read(A.UC_ARM_REG_R1)))
   result=cb_result
  elif pc==(0x4ca83c if stock else 0x101000):events.append(('read',));result=-5
  elif pc==(0x4d09b4 if stock else 0x101010):events.append(('assert',));result=1
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cb5ac if stock else sy['g2_lfs_dir_traverse'])|1,0,count=2000)
 assert done[0],(stock,tags,events)
 return u.reg_read(A.UC_ARM_REG_R0),events
n=0
for tags in ((),(0x40100000,),(0x40100000,0x20200408),(0x4ff00000,0x20100403)):
 for mask,wanted in ((0,0),(0x70000000,0x20000000),(0x400ffc00,0)):
  for result in (0,1,-5):
   a=run(True,tags,mask,wanted,result);b=run(False,tags,mask,wanted,result)
   assert a==b,(tags,mask,wanted,result,a,b);n+=1
print('PASS_DIR_TRAVERSE',n)
