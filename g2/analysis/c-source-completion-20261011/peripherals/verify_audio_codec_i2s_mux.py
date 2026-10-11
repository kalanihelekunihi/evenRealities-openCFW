#!/usr/bin/env python3
"""Original-byte/C I2S clock mux dispatch oracle."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_i2s_source_mux_candidate/mux.c';O=D/'codec-i2s-mux-m4.o';L=D/'codec-i2s-mux-lower-m4.o';E=D/'codec-i2s-mux-oracle.elf';stub=D/'codec-i2s-mux-lower.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline)) uint32_t g2_codec_clock_mux_request(uint32_t a,uint32_t b){return a+b;}\n')
for s,o in ((S,O),(stub,L)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O),str(L)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def run(original,instance,mode):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 u.reg_write(A.UC_ARM_REG_R0,instance);u.reg_write(A.UC_ARM_REG_R1,mode);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 calls=[];done=[False];child=0x539bbc if original else sym['g2_codec_clock_mux_request']&~1
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop()
  elif pc==child:
   calls.append((c.reg_read(A.UC_ARM_REG_R0),c.reg_read(A.UC_ARM_REG_R1)));c.reg_write(A.UC_ARM_REG_R0,0);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x58fd7e if original else sym['g2_codec_source_mux'])|1,0,count=100)
 assert done[0]
 return calls
n=0
for instance in (0,1,2):
 for mode in (0,1,2,3,255):
  a=run(True,instance,mode);b=run(False,instance,mode);assert a==b,(instance,mode,a,b);n+=1
print('PASS_AUDIO_CODEC_I2S_MUX',n)
for p in (O,L,E,stub):p.unlink()
