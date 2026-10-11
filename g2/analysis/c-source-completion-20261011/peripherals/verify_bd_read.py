#!/usr/bin/env python3
"""Bounded stock/source LittleFS read cache state-machine oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_sync_candidate';E=D/'bd-read-oracle.elf'
for name in ('bd_read','bd_flush_leaves'):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-c',str(S/(name+'.c')),'-o',str(D/(name+'-read-m4.o'))],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',
 '--defsym=g2_lfs_memcpy=0x101011','--defsym=g2_file_close_error=0x101021',
 '--defsym=g2_lfs_cache_fill=0x101031','-o',str(E),
 str(D/'bd_read-read-m4.o'),str(D/'bd_flush_leaves-read-m4.o')],
 check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,mode,size,read_error):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
 fs=0x20010000;pc=0x20011000;rc=0x20012000;cfg=0x20013000
 pb=0x20014000;rb=0x20015000;out=0x20016000;stack=0x200f0000
 w(fs+0x68,cfg);w(fs+0x6c,10);w(cfg+4,0x101101);w(cfg+0x14,8);w(cfg+0x1c,256);w(cfg+0x28,16)
 for c,b in ((pc,pb),(rc,rb)):
  w(c,0xffffffff);w(c+4,0);w(c+8,0);w(c+12,b)
 u.mem_write(pb,bytes(range(16)));u.mem_write(rb,bytes(range(16,32)))
 if mode=='pcache':w(pc,2);w(pc+4,0);w(pc+8,16)
 if mode=='rcache':w(rc,2);w(rc+4,0);w(rc+8,16)
 hint=1 if mode=='direct' else 16
 for i,v in enumerate((2,0,out,size)):w(stack+i*4,v)
 for reg,v in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,pc),(A.UC_ARM_REG_R2,rc),
               (A.UC_ARM_REG_R3,hint),(A.UC_ARM_REG_SP,stack),(A.UC_ARM_REG_LR,0x101181)):
  u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,addr,sz,user):
  if addr==0x101180:done[0]=True;cpu.emu_stop();return
  old={0x439be4:'copy',0x101100:'read',0x4d09b4:'error'}
  new={0x101010:'copy',0x101100:'read',0x101020:'error'}
  name=(old if stock else new).get(addr)
  if name is None:return
  if name=='error':raise AssertionError('unexpected error diagnostic')
  regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
  if name=='copy':
   events.append(('copy',regs[2]))
   cpu.mem_write(regs[0],bytes(cpu.mem_read(regs[1],regs[2])))
   result=regs[0]
  else:
   count=rd(cpu.reg_read(A.UC_ARM_REG_SP))
   events.append(('read',regs[1],regs[2],count))
   if read_error==0:cpu.mem_write(regs[3],bytes(range(40,40+count)))
   result=read_error
  cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
  cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4ca83c if stock else sy['g2_lfs_bd_read'])|1,0,count=800)
 assert done[0],(stock,mode,size)
 return events,u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(out,32)),tuple(rd(rc+i) for i in (0,4,8))
count=0
for mode in ('pcache','rcache','direct','miss'):
 for size in (0,1,7,8,13):
  for error in (0,-5):
   a=run(True,mode,size,error);b=run(False,mode,size,error)
   assert a==b,(mode,size,error,a,b)
   count+=1
print('PASS_BD_READ',count)
