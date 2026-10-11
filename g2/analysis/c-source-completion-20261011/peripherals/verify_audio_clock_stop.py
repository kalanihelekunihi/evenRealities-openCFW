#!/usr/bin/env python3
"""Original-byte/C private audio clock pin teardown comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/audio_clock_stop_source_candidate/stop.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'stop.o';e=t/'stop.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_audio_clock_pin_config=0x78ee48','--defsym=g2_codec_pin_function=0x101011','-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(native,group,mode):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.reg_write(A.UC_ARM_REG_R0,group);u.reg_write(A.UC_ARM_REG_R1,mode);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  child=0x480f0c if native else 0x101010;calls=[];done=[False]
  def code(c,pc,_sz,_d):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   if pc==child:
    calls.append((c.reg_read(A.UC_ARM_REG_R0),c.reg_read(A.UC_ARM_REG_R1)))
    c.reg_write(A.UC_ARM_REG_R0,0);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x4c3138 if native else sym['audio_clock_stop'])|1,0,count=200)
  assert done[0]
  return calls
 n=0
 for group in (0,1,2,3,255):
  for mode in (0,1,2,255,256,0xffffffff):
   a=run(True,group,mode);b=run(False,group,mode)
   assert a==b,(group,mode,a,b)
   n+=1
 print('PASS_AUDIO_CLOCK_STOP',n)
