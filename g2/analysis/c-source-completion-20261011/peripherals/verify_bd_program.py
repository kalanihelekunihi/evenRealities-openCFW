#!/usr/bin/env python3
"""Bounded original/source LittleFS cached program transitions."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate/bd_program.c';O=D/'bd-program-m4.o';E=D/'bd-program-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
low={'g2_lfs_aligndown':0x101001,'g2_lfs_memcpy':0x101011,
     'g2_lfs_bd_flush':0x101021,'g2_file_close_error':0x101031}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in low.items()],'-o',str(E),str(O)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
old={0x4ca708:'align',0x439be4:'copy',0x4caafa:'flush',0x4d09b4:'error'}
new={0x101000:'align',0x101010:'copy',0x101020:'flush',0x101030:'error'}
def run(stock,mode,size,flush_err):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 fs=0x20010000;pc=0x20011000;rc=0x20012000;cfg=0x20013000;pb=0x20014000;data=0x20015000;stack=0x200f0000
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(fs+0x68,cfg);w(fs+0x6c,20);w(cfg+0x18,8);w(cfg+0x1c,256);w(cfg+0x28,16)
 w(pc,5 if mode=='hit' else 0xffffffff);w(pc+4,0);w(pc+8,4);w(pc+12,pb)
 u.mem_write(data,b'abcdefgh');u.mem_write(pb,b'X'*32)
 for i,v in enumerate((5,8,data,size)):w(stack+i*4,v)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,pc),(A.UC_ARM_REG_R2,rc),
               (A.UC_ARM_REG_R3,1),(A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,addr,sz,user):
  if addr==0x101180:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(addr)
  if not name:return
  regs=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='align':events.append((name,regs[0],regs[1]));result=(regs[0]//regs[1])*regs[1]
  elif name=='copy':
   events.append((name,regs[2]));cpu.mem_write(regs[0],bytes(cpu.mem_read(regs[1],regs[2])));result=regs[0]
  elif name=='flush':events.append((name,regs[:3]));result=flush_err
  else:events.append((name,regs[2]));result=1
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cac04 if stock else sy['g2_lfs_bd_program'])|1,0,count=300)
 assert done[0],(stock,mode,size,events)
 return events,u.reg_read(A.UC_ARM_REG_R0),tuple(rd(pc+x) for x in (0,4,8)),bytes(u.mem_read(pb,32))
count=0
for mode in ('hit','miss'):
 for size in (0,1,4,8):
  for err in (0,-5):
   a=run(True,mode,size,err);b=run(False,mode,size,err)
   assert a==b,(mode,size,err,a,b)
   count+=1
print('PASS_BD_PROGRAM',count)
