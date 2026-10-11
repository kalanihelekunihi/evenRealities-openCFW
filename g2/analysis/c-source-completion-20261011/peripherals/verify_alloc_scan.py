#!/usr/bin/env python3
"""Bounded original/source LittleFS lookahead callback/scan."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_sync_candidate';E=D/'alloc-scan-oracle.elf'
objs=[]
for name in ('alloc_scan','alloc_checkpoint','cache_fill'):
 o=D/(name+'-scan-m4.o');objs.append(o)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S/(name+'.c')),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_fs_traverse=0x101001','-o',str(E),*[str(o) for o in objs]],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,which,block,next_value,checkpoint,error):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;cfg=0x20011000;buf=0x20012000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x54,7);w(fs+0x58,12);w(fs+0x5c,next_value);w(fs+0x60,checkpoint)
 w(fs+0x64,buf);w(fs+0x68,cfg);w(fs+0x6c,20);w(cfg+0x2c,2)
 u.mem_write(buf,b'\xaa\xbb')
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,block),
               (A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cf284 if stock else 0x101000):
   events.append(('traverse',cpu.reg_read(A.UC_ARM_REG_R3)))
   cpu.reg_write(A.UC_ARM_REG_R0,error&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 addr=(0x4cb0f6 if which=='callback' else 0x4cb12e) if stock else sy['g2_lfs_alloc_lookahead' if which=='callback' else 'g2_lfs_alloc_scan']
 u.emu_start(addr|1,0,count=500)
 assert done[0],(stock,which,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),tuple(rd(fs+x) for x in (0x54,0x58,0x5c,0x60)),bytes(u.mem_read(buf,2))
count=0
for block in (0,7,8,16,19):
 a=run(True,'callback',block,1,12,0);b=run(False,'callback',block,1,12,0)
 assert a==b,('callback',block,a,b);count+=1
for next_value in (0,3,7):
 for checkpoint in (1,12,20):
  for err in (0,-5):
   a=run(True,'scan',0,next_value,checkpoint,err);b=run(False,'scan',0,next_value,checkpoint,err)
   assert a==b,('scan',next_value,checkpoint,err,a,b);count+=1
print('PASS_ALLOC_SCAN',count)
