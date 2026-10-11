#!/usr/bin/env python3
"""Original-byte/C oracle for the bounded I2S handle acquisition body."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_i2s_acquire_source_candidate/acquire.c'
O=D/'codec-i2s-acquire-m4.o';E=D/'codec-i2s-acquire-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_codec_i2s_handle_pool=0x20071114','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def run(original,instance,cell,flags):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segments:u.mem_write(a,b)
 row=0x20071114+(instance if instance<2 else 0)*100
 put(u,row,flags);put(u,row+4,0x12345678);put(u,0x20003000,0xdeadbeef)
 u.reg_write(A.UC_ARM_REG_R0,instance);u.reg_write(A.UC_ARM_REG_R1,0x20003000 if cell else 0);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 writes=[];done=[False]
 def stop(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop()
 def write(_c,_a,a,size,v,_):
  if 0x20071114<=a<0x200711dc or a==0x20003000:writes.append((a,size,v&((1<<(size*8))-1)))
 u.hook_add(UC_HOOK_CODE,stop);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x59005e if original else sym['g2_codec_i2s_acquire'])|1,0,count=200)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),writes,get(u,row),get(u,row+4),get(u,0x20003000)
n=0
for instance in (0,1,2,3):
 for cell in (False,True):
  for flags in (0,0x01000000,0x02000000,0xff000123):
   a=run(True,instance,cell,flags);b=run(False,instance,cell,flags)
   assert a==b,(instance,cell,flags,a,b)
   n+=1
print('PASS_AUDIO_CODEC_I2S_ACQUIRE',n)
for p in (O,E):p.unlink()
