#!/usr/bin/env python3
"""Bounded stock/source oracle for first metadata-pair traversal paths."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/fs_traverse.c';O=D/'fs-traverse-m4.o';E=D/'fs-traverse-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_tortoise_detectcycles=0x101001','--defsym=g2_lfs_dir_fetch=0x101011','--defsym=g2_lfs_dir_getslice=0x101031','--defsym=g2_lfs_ctz_traverse=0x101041','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,fail_visit,fetch_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x10000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 sp=0x2000f000
 for reg,v in ((A.UC_ARM_REG_R0,0x20001000),(A.UC_ARM_REG_R1,0x101021),(A.UC_ARM_REG_R2,0x20004000),(A.UC_ARM_REG_R3,1),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 calls=[];done=[False];seen=[0]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cef18 if stock else 0x101000):
   p=cpu.reg_read(A.UC_ARM_REG_R0);q=cpu.reg_read(A.UC_ARM_REG_R1)
   calls.append(('cycle',tuple(int.from_bytes(cpu.mem_read(p+24+4*i,4),'little') for i in range(2)),tuple(int.from_bytes(cpu.mem_read(q+4*i,4),'little') for i in range(4))))
   result=0
  elif pc==(0x4cbedc if stock else 0x101010):
   calls.append(('fetch',));result=fetch_err
  elif pc==0x101020:
   seen[0]+=1;calls.append(('visit',cpu.reg_read(A.UC_ARM_REG_R1)))
   result=-5 if seen[0]==fail_visit else 0
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cf284 if stock else sy['g2_lfs_fs_traverse'])|1,0,count=400)
 assert done[0],(stock,calls)
 return u.reg_read(A.UC_ARM_REG_R0),calls
n=0
for fv in (1,2,0):
 for fe in (-5,-84):
  a=run(True,fv,fe);b=run(False,fv,fe)
  assert a==b,(fv,fe,a,b)
  n+=1
print('PASS_FS_TRAVERSE',n)
