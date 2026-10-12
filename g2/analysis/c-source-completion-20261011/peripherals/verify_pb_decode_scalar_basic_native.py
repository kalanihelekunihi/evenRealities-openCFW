#!/usr/bin/env python3
"""Actual C/native bool and fixed-width input bytes and stream effects."""
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
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_bool_4901cc',str(S/'display_pb_decode_scalar_basic.c'),str(S/'display_pb_decode_stream.c'),str(S/'display_pb_decode_tag.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,kind,data):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;source=0x20080100;out=0x20080200;it=0x20080300;u.mem_write(source,data);u.mem_write(out,b'\xaa'*8);u.mem_write(it,bytes(40));u.mem_write(it+28,struct.pack('<I',out))
  cb=sy['audio_pb_buffer_read_48f3a4'] if is_c else 0x48f3a5;u.mem_write(stream,struct.pack('<IIII',cb,source,len(data),0))
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,it if kind=='bool' else out),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  name={'bool':'audio_pb_decode_bool_4901cc','fixed32':'audio_pb_decode_fixed32_490190','fixed64':'audio_pb_decode_fixed64_4901ac'}[kind]
  target=sy[name] if is_c else {'bool':0x4901cc,'fixed32':0x490190,'fixed64':0x4901ac}[kind]
  u.emu_start(target|1,0x600000,count=2000)
  s=bytes(u.mem_read(stream,16));err=struct.unpack_from('<I',s,12)[0]
  msg=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(out,8)),s[4:12],msg
 total=0
 for kind,data in [('bool',b'\0'),('bool',b'\x01'),('bool',b'\x80\x01'),('bool',b''),('fixed32',b'\x12\x34\x56\x78'),('fixed32',b'\x01'),('fixed64',bytes(range(8))),('fixed64',b'\x12')]:
  a=run(False,kind,data);b=run(True,kind,data);assert a==b,(kind,data,a,b);total+=1
print('PASS_PB_DECODE_SCALAR_BASIC_NATIVE',total)
