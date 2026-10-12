#!/usr/bin/env python3
"""Actual C/native nanopb default field state for bounded descriptor types."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_defaults.c'
STUB='unsigned audio_pb_extension_iter_4d93a4(void*a,const void*b){(void)a;(void)b;return 0;} unsigned audio_pb_iter_begin_4d94ba(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_iter_next_4d93d8(void*a){(void)a;return 0;} unsigned audio_pb_read_tag_48f66c(void*a,void*b,void*c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;} unsigned audio_pb_decode_field_48fbe4(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;} void audio_uart_pb_stream_init(void*a,const void*b,unsigned c){(void)a;(void)b;(void)c;} void audio_uart_buffer_zero(void*a,unsigned n,unsigned c){unsigned char*p=a;for(unsigned i=0;i<n;i++)p[i]=(unsigned char)c;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_default_field_48fce2',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,typ):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  it=0x20080000;msg=0x20080100;size=0x20080200;field=0x20080300;desc=0x20080400;table=0x20080500
  u.mem_write(it,bytes(40));u.mem_write(msg,b'\xaa'*32);u.mem_write(size,b'\x55'*4);u.mem_write(field,struct.pack('<I',0x12345678));u.mem_write(desc,bytes(24));u.mem_write(table,bytes(4));u.mem_write(desc+4,struct.pack('<I',table))
  u.mem_write(it+18,struct.pack('<H',8));u.mem_write(it+22,bytes([typ]));u.mem_write(it+24,struct.pack('<III',field,msg,size));u.mem_write(it+36,struct.pack('<I',desc))
  if typ==10:u.mem_write(msg,bytes(4))
  u.reg_write(UC_ARM_REG_R0,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_pb_default_field_48fce2'] if is_c else 0x48fce2)|1,0x600000,count=1000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(msg,32)),bytes(u.mem_read(size,4)),bytes(u.mem_read(field,4))
 for typ in (1,0x11,0x21,0x31,0x81,0xa1,8,9,10):
  a=run(False,typ);b=run(True,typ);assert a==b,(typ,a,b)
print('PASS_PB_DECODE_DEFAULT_FIELD_NATIVE 9')
