#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS relocation commit entry/compact."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_relocatingcommit.c';O=D/'dir-relocatingcommit-m4.o';E=D/'dir-relocatingcommit-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
names=('g2_lfs_fs_pred','g2_lfs_dir_traverse','g2_lfs_dir_commitattr','g2_lfs_dir_commitcrc','g2_lfs_dir_getgstate','g2_lfs_dir_splittingcompact','g2_lfs_cache_drop','g2_lfs_dir_fetch','g2_file_close_error')
args=['arm-none-eabi-ld','-Ttext=0x100000']
for i,name in enumerate(names):args+=['--defsym='+name+'='+hex(0x101001+i*0x10)]
subprocess.run(args+['-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,attrs,compact,pred=-2,split=0,erased=0,traverse=0,crc_err=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20001000;cfg=0x20003000;dir=0x20002000;pa=0x20004000;al=0x20005000;pd=0x20006000;tail=0x20007000;sp=0x200f0000
 w(fs+0x68,cfg);w(fs+0x28,0);w(cfg+0x1c,256);w(cfg+0x18,16)
 u.mem_write(dir,b'\0'*32);w(dir,1);w(dir+4,2);w(dir+20,1);u.mem_write(dir+22,bytes([erased]));w(pa,1);w(pa+4,2);w(tail,5);w(tail+4,6)
 for i,tag in enumerate(attrs):w(al+8*i,tag);w(al+8*i+4,tail)
 w(sp,len(attrs));w(sp+4,pd)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,dir),(A.UC_ARM_REG_R2,pa),(A.UC_ARM_REG_R3,al),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cf40a if stock else 0x101000):
   events.append(('pred',));d=cpu.reg_read(A.UC_ARM_REG_R2);cpu.mem_write(d+23,bytes([split]));result=pred
  elif pc==(0x4cb5ac if stock else 0x101010):events.append(('traverse',));result=traverse
  elif pc==(0x4cc2f2 if stock else 0x101030):events.append(('crc',));result=crc_err
  elif pc==(0x4ca81a if stock else 0x101060):events.append(('drop',));result=0
  elif pc==(0x4cc9a0 if stock else 0x101050):events.append(('compact',));result=compact
  elif pc==(0x4d09b4 if stock else 0x101080):events.append(('assert',));result=1
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4ccb80 if stock else sy['g2_lfs_dir_relocatingcommit'])|1,0,count=2000)
 assert done[0],(stock,events)
 return u.reg_read(A.UC_ARM_REG_R0),events,bytes(u.mem_read(dir,32))
n=0
for attrs in ((),(0x40100000,),(0x4ff00000,),(0x600ffc08,)):
 for compact in (-84,0,1):
  a=run(True,attrs,compact);b=run(False,attrs,compact)
  assert a==b,(attrs,compact,a,b);n+=1
for pred in (-84,-2,0):
 for split in (0,1):
  a=run(True,(0x4ff00000,),0,pred,split);b=run(False,(0x4ff00000,),0,pred,split)
  assert a==b,(pred,split,a,b);n+=1
print('PASS_DIR_RELOCATINGCOMMIT',n)

for traverse in (-5,-28,-84,0):
 for crc_err in (-5,-28,0):
  a=run(True,(),0,erased=1,traverse=traverse,crc_err=crc_err)
  b=run(False,(),0,erased=1,traverse=traverse,crc_err=crc_err)
  assert a==b,(traverse,crc_err,a,b)
  n+=1
print('PASS_DIR_RELOCATINGCOMMIT_ERASED',n)
