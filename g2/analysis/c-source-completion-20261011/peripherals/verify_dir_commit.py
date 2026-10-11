#!/usr/bin/env python3
"""Bounded original/source directory-commit wrapper ABI oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_commit.c';O=D/'dir-commit-m4.o';E=D/'dir-commit-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_dir_orphaningcommit=0x101001','--defsym=g2_lfs_fs_deorphan=0x101011','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,orphans,deorphan):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x10000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 for reg,v in ((A.UC_ARM_REG_R0,0x20001000),(A.UC_ARM_REG_R1,0x20002000),(A.UC_ARM_REG_R2,0x20003000),(A.UC_ARM_REG_R3,2),(A.UC_ARM_REG_SP,0x2000f000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 calls=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4ccf7c if stock else 0x101000):
   calls.append(('orphaning',tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))))
   result=orphans
  elif pc==(0x4cf7ac if stock else 0x101010):
   calls.append(('deorphan',cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
   result=deorphan
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cd388 if stock else sy['g2_lfs_dir_commit'])|1,0,count=100)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),calls
n=0
for orphans in (-84,-5,0,1,2):
 for deorphan in (-84,-5,0,1):
  a=run(True,orphans,deorphan);b=run(False,orphans,deorphan)
  assert a==b,(orphans,deorphan,a,b)
  n+=1
print('PASS_DIR_COMMIT',n)
