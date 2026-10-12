#!/usr/bin/env python3
"""Actual C/native input stream constructor state and callback identity."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_pb_stream_init',str(S/'display_pb_decode_stream_init.c'),str(S/'display_pb_decode_stream.c'),str(S/'display_pb_decode_tag.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,size):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  s=0x20080000;u.mem_write(s,b'\xaa'*16)
  for reg,val in ((UC_ARM_REG_R0,s),(UC_ARM_REG_R1,0x20081000),(UC_ARM_REG_R2,size),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_uart_pb_stream_init'] if is_c else 0x48f49c)|1,0x600000,count=100)
  data=bytes(u.mem_read(s,16));callback=struct.unpack_from('<I',data)[0]
  expected=(sy['audio_pb_buffer_read_48f3a4'] if is_c else 0x48f3a5)
  assert callback==expected,(callback,expected)
  return data[4:]
 for size in (0,1,4096,0xffffffff):
  a=run(False,size);b=run(True,size);assert a==b,(size,a,b)
print('PASS_PB_DECODE_STREAM_INIT_NATIVE 4')
