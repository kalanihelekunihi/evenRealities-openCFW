#!/usr/bin/env python3
"""Original/source LittleFS checkpoint and outline transitions."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/file_sync_candidate';E=D/'file-outline-oracle.elf'
objs=[]
for name in ('alloc_checkpoint','file_outline'):
 o=D/(name+'-m4.o');objs.append(o)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S/(name+'.c')),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_file_relocate=0x101001','-o',str(E),*[str(o) for o in objs]],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,which,err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;file=0x20011000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x6c,37);w(fs+0x60,9);w(file+0x30,0x100000);w(file+0x34,11);w(file+0x3c,2)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,file),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cdd0e if stock else 0x101000):
   events.append(('relocate',cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
   cpu.reg_write(A.UC_ARM_REG_R0,err&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 addr=(0x4cb0e0 if which=='checkpoint' else 0x4cde2c) if stock else sy['g2_lfs_alloc_checkpoint' if which=='checkpoint' else 'g2_lfs_file_outline']
 u.emu_start(addr|1,0,count=100)
 assert done[0]
 return events,(u.reg_read(A.UC_ARM_REG_R0) if which=='outline' else None),tuple(rd(x) for x in (fs+0x60,file+0x30,file+0x3c))
count=0
for which in ('checkpoint','outline'):
 for err in (0,-5):
  a=run(True,which,err);b=run(False,which,err)
  assert a==b,(which,err,a,b)
  count+=1
print('PASS_FILE_OUTLINE',count)
