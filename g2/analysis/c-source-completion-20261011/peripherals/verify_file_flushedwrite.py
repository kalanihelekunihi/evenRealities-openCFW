#!/usr/bin/env python3
"""Bounded stock/source LittleFS flushed-write child and state oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/file_flushedwrite.c';O=D/'file-flushedwrite-m4.o';E=D/'file-flushedwrite-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
lower={'g2_lfs_file_outline':0x101001,'g2_lfs_ctz_find':0x101011,
       'g2_lfs_cache_zero':0x101021,'g2_lfs_alloc_checkpoint':0x101031,
       'g2_lfs_ctz_extend':0x101041,'g2_lfs_bd_program':0x101051,
       'g2_lfs_file_relocate':0x101061}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in lower.items()],'-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cde2c:'outline',0x4cd728:'find',0x4ca822:'zero',0x4cb0e0:'checkpoint',
     0x4cd7d2:'extend',0x4cac04:'program',0x4cdd0e:'relocate'}
new={v&~1:n for n,v in zip(('outline','find','zero','checkpoint','extend','program','relocate'),lower.values())}
def run(stock,mode,n,err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,s in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,s)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;file=0x20011000;cfg=0x20012000;buffer=0x20013000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x68,cfg);w(fs+0x7c,32);w(cfg+0x1c,16)
 w(file+0x28,4);w(file+0x2c,8);w(file+0x34,2);w(file+0x38,5);w(file+0x3c,2)
 flags={'inline':0x100000,'writing':0x20000,'new':0}[mode];w(file+0x30,flags)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,file),(A.UC_ARM_REG_R2,buffer),
               (A.UC_ARM_REG_R3,n),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if not name:return
  regs=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='program':
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   events.append((name,rd(sp),rd(sp+4),rd(sp+12)))
   value=err
  elif name=='extend':
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   w(rd(sp+8),7);w(rd(sp+12),0)
   events.append((name,regs[3],rd(sp)))
   value=0
  else:events.append((name,));value=0
  cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4ce1a0 if stock else sy['g2_lfs_file_flushedwrite'])|1,0,count=1000)
 assert done[0],(stock,mode,n,err,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),tuple(rd(file+x) for x in (0x30,0x34,0x38,0x3c))
count=0
for mode in ('inline','writing','new'):
 for n in (0,1,2,4):
  for err in (0,-5):
   a=run(True,mode,n,err);b=run(False,mode,n,err)
   assert a==b,(mode,n,err,a,b)
   count+=1
print('PASS_FILE_FLUSHEDWRITE',count)
