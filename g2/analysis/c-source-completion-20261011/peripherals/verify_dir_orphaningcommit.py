#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS orphaning-commit entry paths."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_orphaningcommit.c';O=D/'dir-orphaningcommit-m4.o';E=D/'dir-orphaningcommit-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
args=['arm-none-eabi-ld','-Ttext=0x100000']
names=('g2_lfs_file_outline','g2_lfs_file_flush','g2_lfs_dir_relocatingcommit','g2_lfs_dir_getgstate','g2_lfs_dir_gettail','g2_lfs_fs_parent','g2_lfs_fs_pred','g2_lfs_fs_preporphans','g2_lfs_gstate_hasmovehere','g2_lfs_fs_prepmove','g2_log_transport_queue_failure','g2_file_close_error')
for i,name in enumerate(names):args+=['--defsym='+name+'='+hex(0x101001+i*0x10)]
subprocess.run(args+['-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,first,getstate):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20001000;dir=0x20002000;cfg=0x20003000
 w(fs+0x68,cfg);w(fs+0x28,0);w(cfg+0x28,32)
 u.mem_write(dir,b'\0'*32);w(dir,1);w(dir+4,2)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,dir),(A.UC_ARM_REG_R2,0x20004000),(A.UC_ARM_REG_R3,2),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False];rel=[0]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4ccb80 if stock else 0x101020):
   rel[0]+=1
   events.append(('relocate',rel[0],cpu.reg_read(A.UC_ARM_REG_R3) if rel[0]==1 else 1))
   result=first if rel[0]==1 else 0
   if first==2 and rel[0]==1:
    sp=cpu.reg_read(A.UC_ARM_REG_SP);pdir=rd(sp+4)
    w(pdir,3);w(pdir+4,4)
   if first==1 and rel[0]==1:
    ldir=cpu.reg_read(A.UC_ARM_REG_R1);w(ldir,3);w(ldir+4,4)
  elif pc==(0x4cbefc if stock else 0x101030):
   events.append(('getgstate',));result=getstate
  elif pc==(0x4733ee if stock else 0x1010a0):
   events.append(('log',));result=0
  elif pc==(0x4cf4da if stock else 0x101050):
   events.append(('parent',));result=-2
  elif pc==(0x4cf40a if stock else 0x101060):
   events.append(('pred',));result=-2
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4ccf7c if stock else sy['g2_lfs_dir_orphaningcommit'])|1,0,count=1000)
 assert done[0],(stock,events)
 return u.reg_read(A.UC_ARM_REG_R0),events,bytes(u.mem_read(dir,32))
n=0
for first in (-84,-5,0,1,2):
 for getstate in (-84,-5,0):
  a=run(True,first,getstate);b=run(False,first,getstate)
  assert a==b,(first,getstate,a,b)
  n+=1
print('PASS_DIR_ORPHANINGCOMMIT',n)
