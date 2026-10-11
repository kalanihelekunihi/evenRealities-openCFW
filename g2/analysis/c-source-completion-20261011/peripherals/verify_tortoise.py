#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS tortoise state transitions."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/tortoise_detectcycles.c';O=D/'tortoise-m4.o';E=D/'tortoise-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_log_transport_queue_failure=0x101001','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,pair,t):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x10000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 for i,v in enumerate(pair):w(0x20001018+4*i,v)
 for i,v in enumerate(t):w(0x20002000+4*i,v)
 for reg,v in ((A.UC_ARM_REG_R0,0x20001000),(A.UC_ARM_REG_R1,0x20002000),(A.UC_ARM_REG_SP,0x2000f000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 logs=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4733ee if stock else 0x101000):
   logs.append((cpu.reg_read(A.UC_ARM_REG_R2),))
   cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cef18 if stock else sy['g2_lfs_tortoise_detectcycles'])|1,0,count=150)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),tuple(int.from_bytes(u.mem_read(0x20002000+4*i,4),'little') for i in range(4)),logs
n=0
for pair in ((0,1),(1,0),(2,3),(5,8)):
 for t in ((0xffffffff,0xffffffff,1,1),(0,1,1,1),(1,0,1,2),(2,3,2,2),(5,8,3,8)):
  a=run(True,pair,t);b=run(False,pair,t)
  assert a==b,(pair,t,a,b)
  n+=1
print('PASS_TORTOISE',n)
