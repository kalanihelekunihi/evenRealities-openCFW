#!/usr/bin/env python3
"""Bounded original/source LittleFS CTZ extension child/state oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/ctz_extend.c';O=D/'ctz-extend-m4.o';E=D/'ctz-extend-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
names=['g2_lfs_alloc','g2_lfs_bd_erase','g2_lfs_ctz_index','g2_lfs_bd_read',
       'g2_lfs_bd_program','g2_lfs_cache_drop','g2_lfs_debug_bad_block']
lower={n:0x101001+i*0x10 for i,n in enumerate(names)}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in lower.items()],'-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4cb186:'alloc',0x4cad2e:'erase',0x4cd6e4:'index',0x4ca83c:'read',
     0x4cac04:'program',0x4ca81a:'drop',0x4733ee:'debug'}
new={v&~1:k.removeprefix('g2_lfs_').removeprefix('bd_').removeprefix('ctz_').removeprefix('cache_').removeprefix('debug_bad_block') or 'debug' for k,v in lower.items()}
def run(stock,size,alloc_err,erase_err,program_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;cfg=0x20011000;pc=0x20012000;rc=0x20013000;block=0x20014000;off=0x20014004;stack=0x200f0000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x68,cfg);w(cfg+0x1c,64);w(block,0xabcdef);w(off,0xabcdef)
 for i,v in enumerate((size,block,off)):w(stack+i*4,v)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,pc),(A.UC_ARM_REG_R2,rc),
               (A.UC_ARM_REG_R3,9),(A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc_addr,sz,user):
  if pc_addr==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc_addr)
  if not name:return
  regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='alloc':w(regs[1],7);events.append(('alloc',));result=alloc_err
  elif name=='erase':events.append(('erase',regs[1]));result=erase_err
  elif name=='index':
   v=rd(regs[1]);w(regs[1],v)
   events.append(('index',v));result=0
  elif name=='read':
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   events.append(('read',rd(sp),rd(sp+4),rd(sp+12)))
   cpu.mem_write(rd(sp+8),(6).to_bytes(4,'little')[:rd(sp+12)])
   result=0
  elif name=='program':
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   events.append(('program',rd(sp),rd(sp+4),rd(sp+12)))
   result=program_err
  elif name=='drop':events.append(('drop',regs[1]));result=0
  else:events.append(('debug',));result=0
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cd7d2 if stock else sy['g2_lfs_ctz_extend'])|1,0,count=1000)
 assert done[0],(stock,size,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),rd(block),rd(off)
count=0
for size in (0,1,64):
 for ae,ee,pe in ((0,0,0),(-5,0,0),(0,-5,0),(0,0,-5)):
  a=run(True,size,ae,ee,pe);b=run(False,size,ae,ee,pe)
  assert a==b,(size,ae,ee,pe,a,b)
  count+=1
print('PASS_CTZ_EXTEND',count)
