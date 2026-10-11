#!/usr/bin/env python3
"""Controlled pin-call oracle for native I2S clock pin selection."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_i2s_clock_enable_source_candidate/enable.c'
O=D/'codec-clock-enable-m4.o';L=D/'codec-clock-pin-stub-m4.o';E=D/'codec-clock-enable-oracle.elf';stub=D/'codec-clock-pin-stub.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline)) uint32_t g2_codec_pin_function(uint32_t a,uint32_t b){return a+b;}\n')
for s,o in ((S,O),(stub,L)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
args=['arm-none-eabi-ld','-Ttext=0x100000']
for n,a in zip(('0a','0b','0c','0d','1a','1b','1c','1d','1e'),(0x20000114,0x2000011c,0x20000120,0x20000118,0x20000124,0x20000130,0x20000134,0x20000128,0x2000012c)):
 args+=['--defsym=g2_codec_clock_pin_'+n+'='+hex(a)]
subprocess.run(args+['-o',str(E),str(O),str(L)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sym={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def run(original,group,mode):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 for i,a in enumerate((0x20000114,0x2000011c,0x20000120,0x20000118,0x20000124,0x20000130,0x20000134,0x20000128,0x2000012c)):
  u.mem_write(a,(0x1000+i).to_bytes(4,'little'))
 u.reg_write(A.UC_ARM_REG_R0,group);u.reg_write(A.UC_ARM_REG_R1,mode);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
 calls=[];done=[False];lower=0x480f0c if original else sym['g2_codec_pin_function']&~1
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop()
  elif pc==lower:
   a=c.reg_read(A.UC_ARM_REG_R0);b=c.reg_read(A.UC_ARM_REG_R1);calls.append((a,b));c.reg_write(A.UC_ARM_REG_R0,0xabcddcba);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x4c3074 if original else sym['g2_codec_clock_enable'])|1,0,count=300)
 assert done[0]
 return calls
n=0
for group in (0,1,2,3):
 for mode in (0,1,2,0x100,0x101):
  a=run(True,group,mode);b=run(False,group,mode)
  assert a==b,(group,mode,a,b)
  n+=1
print('PASS_AUDIO_CODEC_CLOCK_ENABLE',n)
for p in (O,L,E,stub):p.unlink()
