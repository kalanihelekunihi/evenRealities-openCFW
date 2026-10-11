#!/usr/bin/env python3
"""Bounded stock/source LittleFS flushed-read child and state oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/file_flushedread.c';O=D/'file-flushedread-m4.o';E=D/'file-flushedread-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
lower={'g2_lfs_ctz_find':0x101001,'g2_lfs_dir_getread':0x101011,'g2_lfs_bd_read':0x101021}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in lower.items()],'-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cd728:'ctz',0x4cb3f0:'dir',0x4ca83c:'bd'};new={0x101000:'ctz',0x101010:'dir',0x101020:'bd'}
def run(stock,mode,pos,size,want,child_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;file=0x20011000;cfg=0x20012000;out=0x20013000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x68,cfg);w(cfg+0x1c,16)
 w(file+0x28,4);w(file+0x2c,size);w(file+0x34,pos);w(file+0x38,3);w(file+0x3c,0)
 w(file+4,7)
 if mode=='inline':w(file+0x30,0x100000)
 elif mode=='reading':w(file+0x30,0x40000)
 else:w(file+0x30,0)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,file),(A.UC_ARM_REG_R2,out),
               (A.UC_ARM_REG_R3,want),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if not name:return
  regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='ctz':
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   bp=rd(sp+8);op=rd(sp+12)
   w(bp,5);w(op,0)
   events.append(('ctz',regs[3],rd(sp),rd(sp+4)))
  elif name=='dir':
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   events.append(('dir',rd(sp),rd(sp+4),rd(sp+8),rd(sp+12),rd(sp+20)))
  else:
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   events.append(('bd',regs[3],rd(sp),rd(sp+4),rd(sp+12)))
  cpu.reg_write(A.UC_ARM_REG_R0,child_err&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4ce042 if stock else sy['g2_lfs_file_flushedread'])|1,0,count=600)
 assert done[0],(stock,mode,pos,size,want)
 return events,u.reg_read(A.UC_ARM_REG_R0),tuple(rd(file+x) for x in (0x30,0x34,0x38,0x3c))
count=0
for mode in ('inline','reading','ctz'):
 for pos,size,want in ((0,0,1),(0,3,1),(1,3,1),(1,3,2)):
  for err in (0,-5):
   a=run(True,mode,pos,size,want,err);b=run(False,mode,pos,size,want,err)
   assert a==b,(mode,pos,size,want,err,a,b)
   count+=1
print('PASS_FILE_FLUSHEDREAD',count)
