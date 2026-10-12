#!/usr/bin/env python3
"""Actual C/native pointer decoder diagnostic and preserved-error comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_pointer_field.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_pointer_field_48fb1c',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,existing):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  s=0x20080000;u.mem_write(s,struct.pack('<IIII',0,0,0,0x787c70 if existing else 0))
  for reg,val in ((UC_ARM_REG_R0,s),(UC_ARM_REG_R1,2),(UC_ARM_REG_R2,0x20081000),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_decode_pointer_field_48fb1c'] if is_c else 0x48fb1c)|1,0x600000,count=100)
  err=struct.unpack('<I',bytes(u.mem_read(s+12,4)))[0]
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(err,40)).split(b'\0')[0]
 for existing in (False,True):
  a=run(False,existing);b=run(True,existing);assert a==b,(existing,a,b)
print('PASS_PB_DECODE_POINTER_NATIVE 2')
