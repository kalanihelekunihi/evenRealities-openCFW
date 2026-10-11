#!/usr/bin/env python3
"""Bounded original-byte/compiled-C checks for LittleFS directory split."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/dir_split.c';O=D/'dir-split-m4.o';E=D/'dir-split-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_dir_alloc=0x101001',
 '--defsym=g2_lfs_dir_compact=0x101011','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,root,begin,alloc_result,compact_result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in segs:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
 fs,di,sp=0x20001000,0x20002000,0x200f0000
 u.mem_write(di,b'\x00'*32);w(di,3);w(di+4,4);w(di+0x18,7);w(di+0x1c,8)
 w(fs+0x20,3 if root else 12);w(fs+0x24,4 if root else 13)
 w(sp,0);w(sp+4,begin);w(sp+8,begin+2)
 for reg,val in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,di),(A.UC_ARM_REG_R2,0),(A.UC_ARM_REG_R3,0),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,val)
 events=[];done=[False]
 mapping={(0x4cc502 if stock else 0x101000):'alloc',(0x4cc6ca if stock else 0x101010):'compact'}
 def hook(cpu,pc,size,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop();return
  if pc not in mapping:return
  kind=mapping[pc];events.append(kind)
  if kind=='alloc':
   tail=cpu.reg_read(A.UC_ARM_REG_R1);w(tail,10);w(tail+4,11);result=alloc_result
  else:result=compact_result
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cc600 if stock else sy['g2_lfs_dir_split'])|1,0,count=1000)
 assert done[0],(stock,events)
 return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(di,32)),bytes(u.mem_read(fs+0x20,8)),events
n=0
for root in (0,1):
 for begin in (0,1,3):
  for ar,cr in ((-28,0),(0,-84),(0,0),(0,1)):
   a=run(True,root,begin,ar,cr);b=run(False,root,begin,ar,cr)
   assert a==b,(root,begin,ar,cr,a,b);n+=1
print('PASS_DIR_SPLIT',n)
