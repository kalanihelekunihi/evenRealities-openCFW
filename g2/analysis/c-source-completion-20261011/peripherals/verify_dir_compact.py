#!/usr/bin/env python3
"""Bounded original-byte/compiled-C compaction and relocation checks."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_compact.c';O=D/'dir-compact-m4.o';E=D/'dir-compact-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
names=['g2_lfs_bd_erase','g2_lfs_dir_commitprog','g2_lfs_dir_traverse','g2_lfs_dir_commitattr','g2_lfs_dir_getgstate','g2_lfs_dir_commitcrc','g2_lfs_cache_drop','g2_lfs_alloc','g2_log_transport_queue_failure','g2_file_close_error']
cmd=['arm-none-eabi-ld','-Ttext=0x100000']
for i,name in enumerate(names):cmd+=['--defsym='+name+'='+hex(0x101001+i*0x10)]
subprocess.run(cmd+['-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
stock_addrs=[0x4cad2e,0x4cc200,0x4cb5ac,0x4cc23c,0x4cbefc,0x4cc2f2,0x4ca81a,0x4cb186,0x4733ee,0x4d09b4]
labels=['erase','prog','traverse','attr','gstate','crc','drop','alloc','log','assert']
def run(stock,stage,error,cycles=0,superblock=False,alloc_result=None):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 fs,cfg,di,sp=0x20001000,0x20003000,0x20002000,0x200f0000
 u.mem_write(di,b'\x00'*32)
 w(fs+0x68,cfg);w(cfg+0x1c,256);w(cfg+0x18,16);w(cfg+0x24,cycles)
 w(di,0 if superblock else 3);w(di+4,1 if superblock else 4);w(di+8,1)
 w(di+0x18,0xffffffff);w(di+0x1c,0xffffffff)
 w(sp,0);w(sp+4,0);w(sp+8,0)
 for reg,val in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,di),(A.UC_ARM_REG_R2,0),(A.UC_ARM_REG_R3,0),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,val)
 events=[];done=[False]
 mapping=dict(zip(stock_addrs if stock else [0x101000+i*0x10 for i in range(len(names))],labels))
 def hook(cpu,pc,size,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc not in mapping:return
  kind=mapping[pc];events.append(kind)
  if kind=='crc':
   commit=cpu.reg_read(A.UC_ARM_REG_R1);w(commit+4,16)
  if kind=='alloc':w(cpu.reg_read(A.UC_ARM_REG_R1),9)
  if kind=='alloc':result=error if alloc_result is None else alloc_result
  elif kind==stage and events.count(kind)==1:result=error
  else:result=0
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cc6ca if stock else sy['g2_lfs_dir_compact'])|1,0,count=3000)
 assert done[0],(stock,stage,error,events)
 return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(di,32)),bytes(u.mem_read(fs+0x30,36)),events
n=0
for stage,error in [('erase',-5),('prog',-5),('traverse',-5),('gstate',-5),('crc',-5),('erase',-84),('prog',-84),('traverse',-84),('crc',-84)]:
 for superblock in (False,True):
  a=run(True,stage,error,superblock=superblock);b=run(False,stage,error,superblock=superblock)
  assert a==b,(stage,error,superblock,a,b);n+=1
for superblock in (False,True):
 a=run(True,'none',0,superblock=superblock);b=run(False,'none',0,superblock=superblock)
 assert a==b,('success',superblock,a,b);n+=1
for stage in ('erase','prog','traverse','crc'):
 a=run(True,stage,-84,alloc_result=0);b=run(False,stage,-84,alloc_result=0)
 assert a==b,('recovered',stage,a,b);n+=1
print('PASS_DIR_COMPACT',n)
