#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS commit CRC read/error paths."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_commitcrc.c';O=D/'dir-commitcrc-m4.o';E=D/'dir-commitcrc-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
names=('g2_lfs_bd_read','g2_lfs_bd_crc','g2_lfs_bd_program','g2_lfs_bd_sync','g2_lfs_dir_commitattr')
args=['arm-none-eabi-ld','-Ttext=0x100000']
for i,name in enumerate(names):args+=['--defsym='+name+'='+hex(0x101001+i*0x10)]
subprocess.run(args+['-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,off,read_err,crc_err,attr_err,prog_err,sync_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20001000;cfg=0x20002000;commit=0x20003000
 w(fs+0x68,cfg);w(cfg+0x1c,256);w(cfg+0x18,16);w(cfg+0x28,32);w(fs+0x14,0)
 for i,v in enumerate((7,off,0xffffffff,0xffffffff,off,248)):w(commit+4*i,v)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,commit),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 mapping={(0x4ca83c if stock else 0x101000):('read',read_err),
          (0x4caa88 if stock else 0x101010):('crc',crc_err),
          (0x4cac04 if stock else 0x101020):('prog',prog_err),
          (0x4cabbc if stock else 0x101030):('sync',sync_err),
          (0x4cc23c if stock else 0x101040):('attr',attr_err)}
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc not in mapping:return
  name,result=mapping[pc];events.append(name)
  if name=='read' and not read_err:
   s=cpu.reg_read(A.UC_ARM_REG_SP);cpu.mem_write(rd(s+8),b'\xff')
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cc2f2 if stock else sy['g2_lfs_dir_commitcrc'])|1,0,count=2000)
 assert done[0],(stock,events)
 return u.reg_read(A.UC_ARM_REG_R0),events,bytes(u.mem_read(commit,24))
n=0
cases=((16,-5,0,0,0,0),(16,-84,-5,0,0,0),(16,-84,0,-5,0,0),
       (16,0,0,-5,0,0),(16,0,0,0,-5,0),(240,0,0,0,-5,0))
for case in cases:
 a=run(True,*case);b=run(False,*case)
 assert a==b,(case,a,b);n+=1
print('PASS_DIR_COMMITCRC',n)
