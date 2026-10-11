#!/usr/bin/env python3
"""Bounded original/source LittleFS relocation state and child ABI."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/file_relocate.c';O=D/'file-relocate-m4.o';E=D/'file-relocate-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
lower={'g2_lfs_alloc':0x101001,'g2_lfs_bd_erase':0x101011,'g2_lfs_dir_getread':0x101021,
       'g2_lfs_bd_read':0x101031,'g2_lfs_bd_program':0x101041,
       'g2_lfs_memcpy':0x101051,'g2_lfs_cache_zero':0x101061,
       'g2_lfs_cache_drop':0x101071,'g2_lfs_debug_bad_block':0x101081}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in lower.items()],'-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cb186:'alloc',0x4cad2e:'erase',0x4cb3f0:'dir',0x4ca83c:'read',
     0x4cac04:'program',0x439be4:'copy',0x4ca822:'zero',0x4ca81a:'drop',0x4733ee:'debug'}
new={v&~1:k.removeprefix('g2_lfs_').removeprefix('bd_').removeprefix('file_').replace('dir_getread','dir').replace('memcpy','copy').replace('cache_zero','zero').replace('cache_drop','drop').replace('debug_bad_block','debug') for k,v in lower.items()}
def run(stock,off,inline,alloc_err,erase_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;file=0x20011000;cfg=0x20012000;src=0x20013000;dst=0x20014000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x68,cfg);w(cfg+0x28,8);w(fs+0x10,4);w(fs+0x14,2);w(fs+0x18,8);w(fs+0x1c,src)
 w(file+0x30,0x100000 if inline else 0);w(file+0x38,3);w(file+0x3c,off)
 w(file+0x40,9);w(file+0x44,4);w(file+0x48,8);w(file+0x4c,dst);w(file+4,7)
 u.mem_write(src,b'ABCDEFGH');u.mem_write(dst,b'12345678')
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,file),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if not name:return
  regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='alloc':w(regs[1],5);events.append(('alloc',));result=alloc_err
  elif name=='erase':events.append(('erase',regs[1]));result=erase_err
  elif name=='copy':
   events.append(('copy',regs[2]));cpu.mem_write(regs[0],bytes(cpu.mem_read(regs[1],regs[2])));result=regs[0]
  elif name in ('zero','drop'):
   events.append((name,regs[1]));w(regs[1],0xffffffff);result=0
  elif name in ('dir','read','program'):
   events.append((name,));result=0
  else:events.append((name,));result=0
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cdd0e if stock else sy['g2_lfs_file_relocate'])|1,0,count=500)
 assert done[0],(stock,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),tuple(rd(file+x) for x in (0x30,0x38,0x40,0x44,0x48)),bytes(u.mem_read(dst,8))
count=0
for off in (0,1):
 for inline in (False,True):
  for ae,ee in ((0,0),(-5,0),(0,-5)):
   a=run(True,off,inline,ae,ee);b=run(False,off,inline,ae,ee)
   assert a==b,(off,inline,ae,ee,a,b)
   count+=1
print('PASS_FILE_RELOCATE',count)
