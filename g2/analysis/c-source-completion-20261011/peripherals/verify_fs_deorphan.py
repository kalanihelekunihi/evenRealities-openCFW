#!/usr/bin/env python3
"""Bounded stock/source oracle for LittleFS deorphan entry, fetch, finish."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/fs_deorphan.c';O=D/'fs-deorphan-m4.o';E=D/'fs-deorphan-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
args=['arm-none-eabi-ld','-Ttext=0x100000']
for i,name in enumerate(('g2_lfs_dir_fetch','g2_lfs_fs_parent','g2_lfs_dir_getslice','g2_lfs_gstate_hasmovehere','g2_lfs_fs_prepmove','g2_lfs_dir_orphaningcommit','g2_lfs_dir_getgstate','g2_lfs_fs_preporphans','g2_log_transport_queue_failure')):
 args+=['--defsym='+name+'='+hex(0x101001+i*0x10)]
subprocess.run(args+['-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,orphans,fetch_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20001000;w(fs+0x30,orphans)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,0),(A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc==(0x4cbedc if stock else 0x101000):
   p=cpu.reg_read(A.UC_ARM_REG_R2);events.append(('fetch',rd(p),rd(p+4)))
   if not fetch_err:
    d=cpu.reg_read(A.UC_ARM_REG_R1);w(d+24,0xffffffff);w(d+28,0xffffffff);cpu.mem_write(d+22,b'\x01')
   result=fetch_err
  elif pc==(0x4cf570 if stock else 0x101070):
   events.append(('preporphans',cpu.reg_read(A.UC_ARM_REG_R1)&0xff));result=0
  else:return
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cf7ac if stock else sy['g2_lfs_fs_deorphan'])|1,0,count=2000)
 assert done[0],(stock,events)
 return u.reg_read(A.UC_ARM_REG_R0),events
n=0
for orphan in (0,1,2,0x3ff):
 for err in (-84,-5,0):
  a=run(True,orphan,err);b=run(False,orphan,err)
  assert a==b,(orphan,err,a,b)
  n+=1
print('PASS_FS_DEORPHAN',n)
