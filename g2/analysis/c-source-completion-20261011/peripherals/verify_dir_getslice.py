#!/usr/bin/env python3
"""Bounded original/source LittleFS reverse metadata lookup oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_sync_candidate';E=D/'dir-getslice-oracle.elf'
objs=[]
for name in ('dir_getslice','cache_fill'):
 o=D/(name+'-getslice-m4.o');objs.append(o)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S/(name+'.c')),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_gstate_hasmovehere=0x101001','--defsym=g2_lfs_bd_read=0x101011','-o',str(E),*[str(o) for o in objs]],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,etag,off,mask,wanted,outsize,read_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;dir=0x20011000;out=0x20012000;stack=0x200f0000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(dir,7);w(dir+12,off);w(dir+16,etag);u.mem_write(out,b'X'*32)
 for i,v in enumerate((0,out,outsize)):w(stack+i*4,v)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,dir),(A.UC_ARM_REG_R2,mask),
               (A.UC_ARM_REG_R3,wanted),(A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4caf5c if stock else 0x101000):
   events.append(('state',));result=0
  elif pc==(0x4ca83c if stock else 0x101010):
   sp=cpu.reg_read(A.UC_ARM_REG_SP);offset=rd(sp+4);dst=rd(sp+8);n=rd(sp+12)
   events.append(('read',offset,n))
   if read_err==0:
    cpu.mem_write(dst,(b'\0'*4 if offset==8 else b'abcd')[:n])
   result=read_err
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cb23a if stock else sy['g2_lfs_dir_getslice'])|1,0,count=600)
 assert done[0],(stock,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(out,16))
count=0
for etag,off,mask,wanted in ((0,0,0,0),(0,12,0,0),(0x20100004,16,0x7ff00000,0x20100000),(0x20100004,16,0x7ff00000,0x20200000)):
 for outsize in (0,2,4,8):
  for err in (0,-5):
   a=run(True,etag,off,mask,wanted,outsize,err);b=run(False,etag,off,mask,wanted,outsize,err)
   assert a==b,(hex(etag),off,hex(mask),hex(wanted),outsize,err,a,b)
   count+=1
print('PASS_DIR_GETSLICE',count)
