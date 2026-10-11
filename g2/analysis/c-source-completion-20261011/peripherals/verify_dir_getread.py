#!/usr/bin/env python3
"""Bounded stock/source LittleFS inline directory-cache read oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_getread.c';O=D/'dir-getread-m4.o';E=D/'dir-getread-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
lower={'g2_lfs_memcpy':0x101011,'g2_lfs_aligndown':0x101021,
       'g2_lfs_alignup':0x101031,'g2_lfs_dir_getslice':0x101041}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in lower.items()],'-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x439be4:'copy',0x4ca708:'down',0x4ca714:'up',0x4cb23a:'slice'}
new={0x101010:'copy',0x101020:'down',0x101030:'up',0x101040:'slice'}
def run(stock,mode,size,slice_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;dir=0x20010100;pc=0x20011000;rc=0x20012000;cfg=0x20013000
 pb=0x20014000;rb=0x20015000;out=0x20016000;stack=0x200f0000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x68,cfg);w(cfg+0x14,8);w(cfg+0x1c,256);w(cfg+0x28,16)
 for cache,buf in ((pc,pb),(rc,rb)):
  w(cache,0xffffffff);w(cache+4,0);w(cache+8,0);w(cache+12,buf)
 u.mem_write(pb,b'ABCDEFGHIJKLMNOP');u.mem_write(rb,b'abcdefghijklmnop')
 if mode=='pcache':w(pc,0xfffffffe);w(pc+4,0);w(pc+8,16)
 if mode=='rcache':w(rc,0xfffffffe);w(rc+4,0);w(rc+8,16)
 for i,v in enumerate((16,0xfff7fc00,0x20101c00,0,out,size)):w(stack+i*4,v)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,dir),(A.UC_ARM_REG_R2,pc),
               (A.UC_ARM_REG_R3,rc),(A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,addr,sz,user):
  if addr==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(addr)
  if not name:return
  regs=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='copy':
   events.append((name,regs[2]));cpu.mem_write(regs[0],bytes(cpu.mem_read(regs[1],regs[2])));result=regs[0]
  elif name=='down':events.append((name,regs[0],regs[1]));result=(regs[0]//regs[1])*regs[1]
  elif name=='up':events.append((name,regs[0],regs[1]));result=((regs[0]+regs[1]-1)//regs[1])*regs[1]
  else:
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   cache_off=rd(sp);buf=rd(sp+4);count=rd(sp+8)
   events.append((name,regs[2],regs[3],cache_off,count))
   if slice_err>=0:cpu.mem_write(buf,bytes(range(40,40+count)))
   result=slice_err
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cb3f0 if stock else sy['g2_lfs_dir_getread'])|1,0,count=500)
 assert done[0],(stock,mode,size,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(out,20)),tuple(rd(rc+i) for i in (0,4,8))
count=0
for mode in ('pcache','rcache','miss'):
 for size in (0,1,7,8,13):
  for err in (0,-5):
   a=run(True,mode,size,err);b=run(False,mode,size,err)
   assert a==b,(mode,size,err,a,b)
   count+=1
print('PASS_DIR_GETREAD',count)
