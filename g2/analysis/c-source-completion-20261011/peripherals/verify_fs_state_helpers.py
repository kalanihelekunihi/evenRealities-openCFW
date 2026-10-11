#!/usr/bin/env python3
"""Bounded original/source LittleFS state-helper oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/fs_state_helpers.c';O=D/'fs-state-helpers-m4.o';E=D/'fs-state-helpers-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_dir_getslice=0x101001','--defsym=g2_file_close_error=0x101011','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,which,tag,id=0,pair=(3,4),child=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x10000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20001000;pa=0x20002000;out=0x20003000;dir=0x20004000
 for i,v in enumerate(pair):w(pa+4*i,v)
 w(fs+0x30,tag);w(fs+0x34,11);w(fs+0x38,13)
 for i,v in enumerate((31,37,41)):w(out+4*i,v)
 args={0:(fs,id,pa),1:(fs,id,0),2:(fs,dir,out)}[which]
 for reg,v in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2),args):u.reg_write(reg,v)
 u.reg_write(A.UC_ARM_REG_SP,0x2000f000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cb23a if stock else 0x101000):
   sp=cpu.reg_read(A.UC_ARM_REG_SP);dst=rd(sp+4)
   events.append(('get',cpu.reg_read(A.UC_ARM_REG_R2),cpu.reg_read(A.UC_ARM_REG_R3),rd(sp+8)))
   if child>=0:
    for i,v in enumerate((1,2,3)):w(dst+4*i,v)
   result=child
  elif pc==(0x4d09b4 if stock else 0x101010):
   events.append(('assert',));result=1
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 entry=((0x4cf5ec,0x4cf570,0x4cbefc) if stock else (sy['g2_lfs_fs_prepmove'],sy['g2_lfs_fs_preporphans'],sy['g2_lfs_dir_getgstate']))[which]
 u.emu_start(entry|1,0,count=300)
 assert done[0],(stock,which,events)
 return (u.reg_read(A.UC_ARM_REG_R0) if which else 0,tuple(rd(fs+0x30+4*i) for i in range(3)),tuple(rd(out+4*i) for i in range(3)),events)
n=0
for tag in (0,1,0x4ff00502,0x80000001):
 for id in (0,1,0x3ff):
  if id!=0x3ff:
   a=run(True,0,tag,id);b=run(False,0,tag,id)
  else:
   a=run(True,0,tag,id);b=run(False,0,tag,id)
  assert a==b,(tag,id,a,b);n+=1
for tag in (1,2,0x80000001,0x4ff00501):
 for delta in (1,0xffffffff):
  a=run(True,1,tag,delta);b=run(False,1,tag,delta)
  assert a==b,(tag,delta,a,b);n+=1
for child in (-84,-2,0x7ff0000c):
 a=run(True,2,0,child=child);b=run(False,2,0,child=child)
 assert a==b,(child,a,b);n+=1
print('PASS_FS_STATE_HELPERS',n)
