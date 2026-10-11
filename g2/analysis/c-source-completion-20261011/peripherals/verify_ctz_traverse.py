#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS CTZ traversal child ABI."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/ctz_traverse.c';O=D/'ctz-traverse-m4.o';E=D/'ctz-traverse-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_ctz_index=0x101001','--defsym=g2_lfs_bd_read=0x101011','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,size,index,visit_err,read_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x10000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 sp=0x2000f000
 for i,v in enumerate((size,0x101021,0x20004000)):w(sp+4*i,v)
 for reg,v in ((A.UC_ARM_REG_R0,0x20001000),(A.UC_ARM_REG_R1,0x20002000),(A.UC_ARM_REG_R2,0x20003000),(A.UC_ARM_REG_R3,7),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 calls=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc in (0x4cd6e4 if stock else 0x101000,):
   calls.append(('index',rd(cpu.reg_read(A.UC_ARM_REG_R1))))
   result=index
  elif pc in (0x4ca83c if stock else 0x101010,):
   x=cpu.reg_read(A.UC_ARM_REG_SP);calls.append(('read',cpu.reg_read(A.UC_ARM_REG_R3),rd(x),rd(x+4),rd(x+12)))
   if not read_err:
    out=rd(x+8);w(out,11);w(out+4,13)
   result=read_err
  elif pc==0x101020:
   calls.append(('visit',cpu.reg_read(A.UC_ARM_REG_R1)))
   result=visit_err
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cd974 if stock else sy['g2_lfs_ctz_traverse'])|1,0,count=400)
 assert done[0],(stock,calls)
 return u.reg_read(A.UC_ARM_REG_R0),calls
n=0
for size in (0,1,100):
 for idx in (0,1,2):
  for ve in (0,-5):
   for re in (0,-84):
    a=run(True,size,idx,ve,re);b=run(False,size,idx,ve,re)
    assert a==b,(size,idx,ve,re,a,b)
    n+=1
print('PASS_CTZ_TRAVERSE',n)
