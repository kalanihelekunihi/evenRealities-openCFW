#!/usr/bin/env python3
"""Bounded original/source LittleFS erase callback and return."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/bd_erase.c';O=D/'bd-erase-m4.o';E=D/'bd-erase-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_file_close_error=0x101001','-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,block,result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;cfg=0x20011000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 w(fs+0x68,cfg);w(fs+0x6c,20);w(cfg+0x0c,0x101101)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,block),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc in (0x4d09b4,0x101000):
   events.append(('error',cpu.reg_read(A.UC_ARM_REG_R2)))
   cpu.reg_write(A.UC_ARM_REG_R0,1)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  if pc==0x101100:
   events.append(('erase',cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
   cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cad2e if stock else sy['g2_lfs_bd_erase'])|1,0,count=100)
 assert done[0]
 return events,u.reg_read(A.UC_ARM_REG_R0)
count=0
for block in (0,5,19,20):
 for result in (0,-5,1):
  a=run(True,block,result);b=run(False,block,result)
  assert a==b,(block,result,a,b)
  count+=1
print('PASS_BD_ERASE',count)
