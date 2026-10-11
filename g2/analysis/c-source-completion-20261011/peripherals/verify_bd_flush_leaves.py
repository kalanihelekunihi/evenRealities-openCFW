#!/usr/bin/env python3
"""Original/source LittleFS align, cache zero and fill comparison."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;E=D/'bd-flush-leaves-oracle.elf'
src=R/'g2/components/audio/file_sync_candidate'
for name in ('bd_flush_leaves','cache_fill'):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-O2','-c',str(src/(name+'.c')),
                 '-o',str(D/(name+'-m4.o'))],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),
 str(D/'bd_flush_leaves-m4.o'),str(D/'cache_fill-m4.o')],
 check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];
 sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,which,n=0,align=4):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,s in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):u.mem_map(a,s)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 lfs=0x20010000;cache=0x20011000;cfg=0x20012000;buf=0x20013000
 w(lfs+0x68,cfg);w(cfg+0x28,n);w(cache+12,buf);w(cache,17)
 u.mem_write(buf,b'\x31'*128)
 if which=='zero':a=(0x4ca822 if stock else sy['g2_lfs_cache_zero']);r0,r1=lfs,cache
 elif which=='fill':a=(0x43c0e4 if stock else sy['g2_lfs_cache_fill']);r0,r1=buf,n
 else:a=(0x4ca714 if stock else sy['g2_lfs_alignup']);r0,r1=n,align
 for reg,v in ((A.UC_ARM_REG_R0,r0),(A.UC_ARM_REG_R1,r1),(A.UC_ARM_REG_R2,255),
               (A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101181)):u.reg_write(reg,v)
 done=[False]
 def hook(cpu,pc,sz,user):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(a|1,0,count=1000)
 assert done[0],(stock,which,n,align)
 if which=='align':return u.reg_read(A.UC_ARM_REG_R0)
 return bytes(u.mem_read(buf,128)),int.from_bytes(u.mem_read(cache,4),'little')
count=0
for n in (0,1,2,3,4,7,16,31,64):
 for align in (1,2,4,8,16):
  assert run(True,'align',n,align)==run(False,'align',n,align);count+=1
 for which in ('zero','fill'):
  assert run(True,which,n)==run(False,which,n);count+=1
print('PASS_BD_FLUSH_LEAVES',count)
