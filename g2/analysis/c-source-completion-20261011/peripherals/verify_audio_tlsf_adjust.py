#!/usr/bin/env python3
"""Bounded original-byte/C TLSF align and adjusted size comparisons."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];S=R/'g2/components/audio/tlsf_adjust_request_candidate/adjust.c'
STOCK=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);o=t/'adjust.o';e=t/'adjust.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_file_close_error=0x101011','-o',str(e),str(o)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def string(u,a):return bytes(u.mem_read(a,110)).split(b'\0',1)[0].decode('ascii')
 def run(native,entry,size,align):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(STOCK)+4095)&~4095);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x100000);u.mem_write(0x438000,STOCK)
  if not native:
   for a,b in segs:u.mem_write(a,b)
  u.reg_write(A.UC_ARM_REG_R0,size);u.reg_write(A.UC_ARM_REG_R1,align);u.reg_write(A.UC_ARM_REG_SP,0x200f0000);u.reg_write(A.UC_ARM_REG_LR,0x101181)
  error=0x4d09b4 if native else 0x101010;events=[];done=[False]
  def code(c,pc,_size,_data):
   if pc==0x101180:done[0]=True;c.emu_stop();return
   if pc==error:
    r=[c.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
    events.append((string(c,r[0]),string(c,r[1]),r[2]));c.reg_write(A.UC_ARM_REG_R0,0);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,code)
  addr=(0x4cfec2 if entry=='align' else 0x4cff42) if native else sym['g2_tlsf_align_up' if entry=='align' else 'g2_tlsf_adjust_request']
  u.emu_start(addr|1,0,count=120)
  assert done[0]
  return u.reg_read(A.UC_ARM_REG_R0),events
 n=0
 for entry in ('align','adjust'):
  for size in (0,1,4,11,12,13,16,1000,0x3ffffffc,0x3fffffff,0x40000000,0xffffffff):
   for align in (0,1,2,3,4,8,16):
    a=run(True,entry,size,align);b=run(False,entry,size,align)
    assert a==b,(entry,size,align,a,b)
    n+=1
 print('PASS_AUDIO_TLSF_ADJUST',n)
