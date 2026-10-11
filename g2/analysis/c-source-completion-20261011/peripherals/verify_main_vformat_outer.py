#!/usr/bin/env python3
"""Bounded original-byte/source oracle for Main formatter output and wrapper."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/main/full_formatter_outer_candidate/vformat.c';O=D/'main-vformat-m4.o';E=D/'main-vformat-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_iar_general_format=0x101001','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def machine(stock):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 return u
def w(u,a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def callback(stock,capacity,letters):
 u=machine(stock);ctx=0x20002000;buf=0x20003000;sp=0x200f0000
 u.mem_write(buf,b'\xa5'*32);w(u,ctx,buf);w(u,ctx+4,capacity);w(u,ctx+8,0)
 for byte in letters:
  for reg,val in ((A.UC_ARM_REG_R0,ctx),(A.UC_ARM_REG_R1,byte),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,val)
  done=[False]
  def hook(cpu,pc,size,user):
   if pc==0x101180:done[0]=True;cpu.emu_stop()
  h=u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x439c8a if stock else sy['g2_format_put'])|1,0,count=100)
  u.hook_del(h);assert done[0]
 return bytes(u.mem_read(ctx,12)),bytes(u.mem_read(buf,32))
def wrapper(stock,capacity,core_result,count):
 u=machine(stock);out=0x20002000;fmt=0x20003000;args=0x20004000;sp=0x200f0000
 u.mem_write(out,b'\xa5'*32);u.mem_write(fmt,b'%d\x00');w(u,args,123)
 for reg,val in ((A.UC_ARM_REG_R0,out),(A.UC_ARM_REG_R1,capacity),(A.UC_ARM_REG_R2,fmt),(A.UC_ARM_REG_R3,args),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,val)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc!=(0x481836 if stock else 0x101000):return
  context=cpu.reg_read(A.UC_ARM_REG_R1);events.append((cpu.reg_read(A.UC_ARM_REG_R2),rd(cpu,cpu.reg_read(A.UC_ARM_REG_R3)),rd(cpu,context+4)))
  w(cpu,context+8,count)
  if rd(cpu,context) and rd(cpu,context+4):cpu.mem_write(rd(cpu,context),b'X');w(cpu,context,rd(cpu,context)+1);w(cpu,context+4,rd(cpu,context+4)-1)
  cpu.reg_write(A.UC_ARM_REG_R0,core_result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x44b76c if stock else sy['g2_log_vformat'])|1,0,count=300)
 assert done[0],(stock,capacity,core_result)
 return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(out,32)),events
n=0
for cap in (0,1,2,16):
 for letters in ((),(65,),(65,66,67)):
  a=callback(True,cap,letters);b=callback(False,cap,letters)
  assert a==b,(cap,letters,a,b);n+=1
 for ret in (-7,0,7):
  a=wrapper(True,cap,ret,5);b=wrapper(False,cap,ret,5)
  assert a==b,(cap,ret,a,b);n+=1
print('PASS_MAIN_VFORMAT_OUTER',n)
