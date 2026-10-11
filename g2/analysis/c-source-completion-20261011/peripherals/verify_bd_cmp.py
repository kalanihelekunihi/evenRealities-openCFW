#!/usr/bin/env python3
"""Bounded original/source LittleFS block comparison child ABI."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;E=D/'bd-cmp-oracle.elf'
src=R/'g2/components/audio/file_sync_candidate/bd_cmp.c';obj=D/'bd-cmp-m4.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_bd_read=0x101001',
                '--defsym=g2_lfs_memcmp=0x101011','-o',str(E),str(obj)],
               check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,size,read_err,cmp):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 stack=0x200f0000;data=0x20011000
 for i,v in enumerate((7,0x20012000,size)):u.mem_write(stack+i*4,v.to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,0),
               (A.UC_ARM_REG_R2,0x20010100),(A.UC_ARM_REG_R3,16),
               (A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  names=({0x4ca83c:'read',0x4751c8:'cmp'} if stock else {0x101000:'read',0x101010:'cmp'})
  name=names.get(pc)
  if not name:return
  regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='read':
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   tail=[int.from_bytes(cpu.mem_read(sp+i*4,4),'little') for i in range(4)]
   events.append((name,regs[:3],regs[3],tail[:2],tail[3]))
   result=read_err
  else:
   events.append((name,regs[2]))
   result=cmp
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x4caa04 if stock else sy['g2_lfs_bd_cmp'])|1,0,count=300)
 assert done[0]
 return events,u.reg_read(A.UC_ARM_REG_R0)
count=0
for size in (0,1,8,13):
 for re in (0,-5):
  for cmp in (-1,0,1):
   a=run(True,size,re,cmp);b=run(False,size,re,cmp)
   # Scratch buffer address is compiler-specific; only size and stable ABI are compared.
   assert a==b,(size,re,cmp,a,b)
   count+=1
print('PASS_BD_CMP',count)
