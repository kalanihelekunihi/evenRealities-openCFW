#!/usr/bin/env python3
"""Bounded original/source LittleFS reachable-block count oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/fs_size.c';O=D/'fs-size-m4.o';E=D/'fs-size-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_fs_traverse=0x101001','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,size,error):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x10000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 u.reg_write(A.UC_ARM_REG_R0,0x20001000);u.reg_write(A.UC_ARM_REG_SP,0x2000f000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 seen=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cf284 if stock else 0x101000):
   seen.append(cpu.reg_read(A.UC_ARM_REG_R3))
   cpu.mem_write(cpu.reg_read(A.UC_ARM_REG_R2),int(size).to_bytes(4,'little'))
   cpu.reg_write(A.UC_ARM_REG_R0,error&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cfa12 if stock else sy['g2_lfs_fs_size'])|1,0,count=100)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),seen
n=0
for size in (0,1,100,0x7fffffff):
 for error in (0,-5,-84):
  a=run(True,size,error);b=run(False,size,error)
  assert a==b,(size,error,a,b);n+=1
print('PASS_FS_SIZE',n)
