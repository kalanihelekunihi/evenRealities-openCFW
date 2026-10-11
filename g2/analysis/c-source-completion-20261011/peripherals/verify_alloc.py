#!/usr/bin/env python3
"""Original/source LittleFS lookahead allocation bounded oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/alloc.c';O=D/'alloc-m4.o';E=D/'alloc-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_alloc_scan=0x101001','--defsym=g2_lfs_no_space_log=0x101011','-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,mask,next_value,size,checkpoint,scan_result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;out=0x20011000;buf=0x20012000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x54,6);w(fs+0x58,size);w(fs+0x5c,next_value);w(fs+0x60,checkpoint);w(fs+0x64,buf);w(fs+0x6c,20);w(out,0xabcdef)
 u.mem_write(buf,bytes((mask&255,(mask>>8)&255))+b'\0'*14)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,out),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cb12e if stock else 0x101000):
   events.append(('scan',));cpu.reg_write(A.UC_ARM_REG_R0,scan_result&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  if pc==(0x4733ee if stock else 0x101010):
   events.append(('space',));cpu.reg_write(A.UC_ARM_REG_R0,0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cb186 if stock else sy['g2_lfs_alloc'])|1,0,count=500)
 assert done[0],(stock,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),tuple(rd(x) for x in (out,fs+0x5c,fs+0x60))
count=0
for mask in (0,1,3,0x55,0xff):
 for next_value,size,checkpoint in ((0,8,8),(2,8,8),(7,8,8),(8,8,0),(8,8,4)):
  for scan in (-5,):
   a=run(True,mask,next_value,size,checkpoint,scan);b=run(False,mask,next_value,size,checkpoint,scan)
   assert a==b,(mask,next_value,size,checkpoint,a,b)
   count+=1
print('PASS_ALLOC',count)
