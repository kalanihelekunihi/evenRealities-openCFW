#!/usr/bin/env python3
"""Stock/C pin-function validation, unlock/write order and IRQ restoration."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent
S=R/'g2/components/audio/codec_pin_function_source_candidate/pin.c';O=D/'codec-pin-function-m4.o';L=D/'codec-pin-critical-m4.o';E=D/'codec-pin-function-oracle.elf';stub=D/'codec-pin-critical.c'
stub.write_text('#include <stdint.h>\n__attribute__((noinline)) uint32_t g2_gpio_critical_save(void){return 0;}\n')
for s,o in ((S,O),(stub,L)):
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(o)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O),str(L)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
stock=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def run(original,pin,cfg,irq):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x2000)
 if original:u.mem_write(0x438000,stock)
 else:
  for a,b in segs:u.mem_write(a,b)
 u.reg_write(A.UC_ARM_REG_R0,pin);u.reg_write(A.UC_ARM_REG_R1,cfg);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181);u.reg_write(A.UC_ARM_REG_PRIMASK,irq)
 writes=[];critical=[];done=[False];child=0x473940 if original else sym['g2_gpio_critical_save']&~1
 def hook(c,pc,_s,_):
  if pc==0x101180:done[0]=True;c.emu_stop()
  elif pc==child:
   prior=c.reg_read(A.UC_ARM_REG_PRIMASK);critical.append(prior);c.reg_write(A.UC_ARM_REG_PRIMASK,1);c.reg_write(A.UC_ARM_REG_R0,prior);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
 def written(_cpu,_access,a,size,v,_):
  if 0x40010000<=a<0x40012000:writes.append((a,size,v&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,written)
 u.emu_start((0x480f0c if original else sym['g2_codec_pin_function'])|1,0,count=250)
 assert done[0]
 return u.reg_read(A.UC_ARM_REG_R0),u.reg_read(A.UC_ARM_REG_PRIMASK),critical,writes
n=0
for pin in tuple(range(224))+(224,225,255):
 for cfg in (0,0x400,0x800,0x2000,0x4000,0xc000):
  for irq in (0,1):
   a=run(True,pin,cfg,irq);b=run(False,pin,cfg,irq)
   assert a==b,(pin,cfg,irq,a,b)
   n+=1
print('PASS_AUDIO_CODEC_PIN_FUNCTION',n)
for p in (O,L,E,stub):p.unlink()
