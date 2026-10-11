#!/usr/bin/env python3
"""Stock/C signed halfword PDM clock-source classifier oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_pdm_clock_source_candidate/source.c';O=D/'codec-pdm-clock-source-m4.o';E=D/'codec-pdm-clock-source-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def run(original,x):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 u.reg_write(A.UC_ARM_REG_R0,x&0xffffffff);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 done=[False]
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x591d14 if original else sym['g2_pdm_clock_source'])|1,0,count=100)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0)
values=(-32768,-1,0,1,0xff,0x100,0x101,0x1ff,*range(0x200,0x210),0x7fff,0x10000,0xffffffff)
for x in values:
 a=run(True,x);b=run(False,x);assert a==b,(x,a,b)
print('PASS_AUDIO_CODEC_PDM_CLOCK_SOURCE',len(values))
for p in (O,E):p.unlink()
