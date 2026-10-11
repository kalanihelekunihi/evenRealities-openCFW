#!/usr/bin/env python3
"""Bounded original/source LittleFS file-flush state transition oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/file_flush.c';O=D/'file-flush-m4.o';E=D/'file-flush-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
lower={'g2_lfs_cache_drop':0x101001,'g2_lfs_bd_flush':0x101011,
       'g2_lfs_file_flushedread':0x101021,'g2_lfs_file_flushedwrite':0x101031,
       'g2_lfs_file_relocate':0x101041,'g2_lfs_debug_bad_block':0x101051}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',
               *[f'--defsym={k}={v:#x}' for k,v in lower.items()],
               '-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4ca81a:'drop',0x4caafa:'flush',0x4ce042:'read',0x4ce1a0:'write',
     0x4cdd0e:'relocate',0x4733ee:'debug'}
new={v&~1:n for n,v in zip(('drop','flush','read','write','relocate','debug'),lower.values())}
def run(stock,flags,pos,size,flush_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;file=0x20011000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs,0xffffffff);w(file+0x28,3);w(file+0x2c,size);w(file+0x30,flags)
 w(file+0x34,pos);w(file+0x38,4);w(file+0x40,5)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,file),
               (A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if not name:return
  r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='drop':
   events.append((name,r[1]));w(r[1],0xffffffff);value=0xffffffff
  elif name=='flush':events.append((name,r[1],r[2],r[3]));value=flush_err
  elif name=='read':
   events.append((name,r[3]));cpu.mem_write(r[2],b'X');value=1
  elif name=='write':
   events.append((name,r[3]));w(file+0x34,rd(file+0x34)+1);value=1
  else:events.append((name,));value=0
  cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cde54 if stock else sy['g2_lfs_file_flush'])|1,0,count=1500)
 assert done[0],(stock,flags,pos,size,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),tuple(rd(file+x) for x in (0x28,0x2c,0x30,0x34,0x38,0x40))
count=0
for flags in (0,0x40000,0x40000|0x100000,0x20000|0x100000,0x20000):
 for pos,size in ((0,0),(2,2),(2,3)):
  for err in (0,-5):
   a=run(True,flags,pos,size,err);b=run(False,flags,pos,size,err)
   assert a==b,(hex(flags),pos,size,err,a,b)
   count+=1
print('PASS_FILE_FLUSH',count)
