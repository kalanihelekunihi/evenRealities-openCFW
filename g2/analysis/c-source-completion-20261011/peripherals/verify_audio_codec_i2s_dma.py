#!/usr/bin/env python3
"""Original-byte/C I2S DMA configuration MMIO oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_i2s_dma_configure_source_candidate/dma.c';O=D/'codec-i2s-dma-m4.o';E=D/'codec-i2s-dma-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def run(original,valid,mode,instance,seed):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40208000,0x3000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 h=0x20002000;c=0x20003000;d=0x20004000;base=0x40208000+instance*0x1000
 put(u,h,0x01125125 if valid else 0xdeadbeef);put(u,h+4,instance)
 for i in range(6):put(u,d+4*i,seed+0x101*i)
 u.mem_write(c+1,bytes([mode]));put(u,base+0x200,seed)
 u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_R1,c);u.reg_write(A.UC_ARM_REG_R2,d);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 writes=[];done=[False]
 def stop(cpu,pc,_s,_):
  if pc==0x101180:done[0]=True;cpu.emu_stop()
 def written(_cpu,_access,a,size,v,_):
  if 0x40208000<=a<0x4020b000:writes.append((a,size,v&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,stop);u.hook_add(UC_HOOK_MEM_WRITE,written)
 u.emu_start((0x590a24 if original else sym['g2_codec_i2s_dma_configure'])|1,0,count=500)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),writes,bytes(u.mem_read(h,100)),bytes(u.mem_read(c,40)),bytes(u.mem_read(base,0x310))
n=0
for valid in (False,True):
 for mode in (0,1,2,3,255):
  for instance in (0,1):
   for seed in (0,0x12345678,0xffffffff):
    a=run(True,valid,mode,instance,seed);b=run(False,valid,mode,instance,seed)
    assert a==b,(valid,mode,instance,seed,a[:2],b[:2])
    n+=1
print('PASS_AUDIO_CODEC_I2S_DMA',n)
for p in (O,E):p.unlink()
