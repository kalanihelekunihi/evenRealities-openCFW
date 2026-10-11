#!/usr/bin/env python3
"""Original-byte/C PDM clock configuration write oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_pdm_clock_prepare_source_candidate/prepare.c';O=D/'codec-pdm-clock-prepare-m4.o';E=D/'codec-pdm-clock-prepare-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def run(original,valid,instance,value):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40201000,0x5000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 h=0x20002000;put(u,h,0x01f956e2 if valid else 0xdeadbeef);put(u,h+8,instance)
 u.reg_write(A.UC_ARM_REG_R0,h);u.reg_write(A.UC_ARM_REG_R1,value);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 writes=[];done=[False]
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop()
 def written(_c,_a,a,size,v,_):
  if 0x40201000<=a<0x40206000:writes.append((a,size,v&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,written)
 u.emu_start((0x592462 if original else sym['g2_pdm_prepare_clock'])|1,0,count=100)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),writes
n=0
for valid in (False,True):
 for instance in (0,1,2,3):
  for value in (0,1,16,0xffffffff):
   a=run(True,valid,instance,value);b=run(False,valid,instance,value);assert a==b,(valid,instance,value,a,b);n+=1
print('PASS_AUDIO_CODEC_PDM_CLOCK_PREPARE',n)
for p in (O,E):p.unlink()
