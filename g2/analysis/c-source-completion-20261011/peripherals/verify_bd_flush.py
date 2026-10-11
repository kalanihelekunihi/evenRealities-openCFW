#!/usr/bin/env python3
"""Bounded stock/source LittleFS block flush child and return oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
O='/tmp/g2logtransport-check/bd_flush.o';E=D/'bd-flush-oracle.elf'
addrs={'g2_lfs_alignup':0x101001,'g2_lfs_bd_cmp':0x101011,
       'g2_lfs_cache_zero':0x101021,'g2_lfs_cache_drop':0x101031,
       'g2_file_close_error':0x101041}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',
                *[f'--defsym={k}={v:#x}' for k,v in addrs.items()],
                '-o',str(E),O],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4ca714:'align',0x4ca81a:'drop',0x4caa04:'cmp',0x4ca822:'zero',0x4d09b4:'error',0x101100:'prog'}
new={0x101000:'align',0x101030:'drop',0x101010:'cmp',0x101020:'zero',0x101040:'error',0x101100:'prog'}
def run(stock,block,validate,prog_result,cmp_result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little',signed=False))
 lfs=0x20010000;pc=0x20011000;rc=0x20012000;cfg=0x20013000
 w(lfs+0x68,cfg);w(lfs+0x6c,100);w(cfg+8,0x101101);w(cfg+0x18,16)
 w(pc,block);w(pc+4,32);w(pc+8,9);w(pc+12,0x20014000)
 for reg,v in ((A.UC_ARM_REG_R0,lfs),(A.UC_ARM_REG_R1,pc),(A.UC_ARM_REG_R2,rc),
               (A.UC_ARM_REG_R3,validate),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,addr,sz,user):
  if addr==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(addr)
  if name is None:return
  if name=='error':raise AssertionError('unexpected diagnostic')
  regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='align':result=16;events.append((name,regs[0],regs[1]))
  elif name=='prog':
   result=prog_result;events.append((name,tuple(regs),int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),'little')))
  elif name=='cmp':result=cmp_result;events.append((name,tuple(regs)))
  else:result=0;events.append((name,tuple(regs[:2])))
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4caafa if stock else sy['g2_lfs_bd_flush'])|1,0,count=300)
 assert done[0]
 return events,u.reg_read(A.UC_ARM_REG_R0)
count=0
for block in (0xffffffff,0xfffffffe,5):
 for validate in (0,1):
  for prog in (0,-5):
   for cmp in (0,1,-7):
    a=run(True,block,validate,prog,cmp);b=run(False,block,validate,prog,cmp)
    assert a==b,(block,validate,prog,cmp,a,b)
    count+=1
print('PASS_BD_FLUSH',count)
