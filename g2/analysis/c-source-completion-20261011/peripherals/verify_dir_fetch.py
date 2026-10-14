#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS dir fetch entry/error paths."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_fetch.c';O=D/'dir-fetch-m4.o';E=D/'dir-fetch-oracle.elf'
G=R/'g2/components/audio/file_sync_candidate/gstate_hasmovehere.c';GO=D/'dir-fetch-gstate-m4.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(G),'-o',str(GO)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_bd_read=0x101011','--defsym=g2_log_transport_queue_failure=0x101021','-o',str(E),str(O),str(GO)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,blocks,pair,errors,disk=None):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20001000;cfg=0x20003000;dir=0x20002000;pa=0x20004000
 w(fs+0x68,cfg);w(fs+0x6c,blocks);w(cfg+0x1c,256);w(cfg+0x18,16)
 w(pa,pair[0]);w(pa+4,pair[1]);u.mem_write(dir,b'X'*32)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,dir),(A.UC_ARM_REG_R2,pa),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 calls=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4ca83c if stock else 0x101010):
   sp=cpu.reg_read(A.UC_ARM_REG_SP);block=rd(sp);off=rd(sp+4);n=rd(sp+12)
   calls.append(('read',block,off,n))
   result=errors[min(len([x for x in calls if x[0]=='read'])-1,len(errors)-1)]
   if disk is not None:
    dst=rd(sp+8)
    if block<len(disk) and off+n<=len(disk[block]):cpu.mem_write(dst,bytes(disk[block][off:off+n]));result=0
    else:result=-84
  elif pc==(0x4733ee if stock else 0x101020):
   calls.append(('log',));result=0
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cbedc if stock else sy['g2_lfs_dir_fetch'])|1,0,count=10000)
 assert done[0],(stock,calls)
 return u.reg_read(A.UC_ARM_REG_R0),calls,bytes(u.mem_read(dir,32))
n=0
for blocks,pair in ((5,(7,1)),(5,(0,1)),(0,(7,1))):
 for errors in ((-5,),(-84,-5),(-84,-84)):
  a=run(True,blocks,pair,errors);b=run(False,blocks,pair,errors)
  assert a==b,(blocks,pair,errors,a,b)
  n+=1
print('PASS_DIR_FETCH',n)

# A valid single-commit directory image checks CRC and metadata state.
def crc32(crc,data):
 tab=(0,0x1db71064,0x3b6e20c8,0x26d930ac,0x76dc4190,0x6b6b51f4,0x4db26158,0x5005713c,0xedb88320,0xf00f9344,0xd6d6a3e8,0xcb61b38c,0x9b64c2b0,0x86d3d2d4,0xa00ae278,0xbdbdf21c)
 for b in data:crc=(crc>>4)^tab[(crc^b)&15];crc=(crc>>4)^tab[(crc^(b>>4))&15]
 return crc
blocks=[bytearray(b'\xff'*256) for _ in range(2)]
blocks[0][0:4]=(1).to_bytes(4,'little');blocks[1][0:4]=(0).to_bytes(4,'little')
tag=0x500ffc04;raw=(tag^0xffffffff).to_bytes(4,'big');blocks[0][4:8]=raw
checksum=crc32(crc32(0xffffffff,blocks[0][0:4]),raw)
blocks[0][8:12]=checksum.to_bytes(4,'little')
a=run(True,2,(0,1),(0,),blocks);b=run(False,2,(0,1),(0,),blocks)
assert a==b,(a,b)
print('PASS_DIR_FETCH_COMMIT',1)
