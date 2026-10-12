#!/usr/bin/env python3
"""Actual compiled C/native nanopb bytes, string, and fixed-bytes effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
STUB='void audio_uart_buffer_zero(void*p,unsigned n,unsigned c){unsigned char*b=p;for(unsigned i=0;i<n;i++)b[i]=(unsigned char)c;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_bytes_490358',str(S/'display_pb_decode_text_fields.c'),str(S/'display_pb_decode_stream.c'),str(S/'display_pb_decode_tag.c'),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,kind,data,size,typ):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;source=0x20080100;out=0x20080200;it=0x20080300
  u.mem_write(source,data);u.mem_write(out,b'\xaa'*64);u.mem_write(it,bytes(40));u.mem_write(it+18,struct.pack('<H',size));u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<I',out))
  cb=sy['audio_pb_buffer_read_48f3a4'] if is_c else 0x48f3a5;u.mem_write(stream,struct.pack('<IIII',cb,source,len(data),0))
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,it),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  name={'bytes':'audio_pb_decode_bytes_490358','string':'audio_pb_decode_string_4903ea','fixed':'audio_pb_decode_extension_49053c'}[kind]
  addr={'bytes':0x490358,'string':0x4903ea,'fixed':0x49053c}[kind]
  u.emu_start((sy[name] if is_c else addr)|1,0x600000,count=5000)
  s=bytes(u.mem_read(stream,16));err=struct.unpack_from('<I',s,12)[0];msg=bytes(u.mem_read(err,50)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(out,64)),s[4:12],msg
 cases=[('bytes',b'\0',8,6),('bytes',b'\x03abc',8,6),('bytes',b'\x03abc',4,6),('bytes',b'\x80\x80\x04',8,6),('string',b'\0',8,7),('string',b'\x03abc',8,7),('string',b'\x03abc',3,7),('fixed',b'\0',4,11),('fixed',b'\x04abcd',4,11),('fixed',b'\x03abc',4,11)]
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
print('PASS_PB_DECODE_TEXT_FIELDS_NATIVE',len(cases))
