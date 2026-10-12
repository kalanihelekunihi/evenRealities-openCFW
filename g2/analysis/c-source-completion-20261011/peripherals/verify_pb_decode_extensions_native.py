#!/usr/bin/env python3
"""Actual C/native extension-list and default descriptor lookup effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
STUB='unsigned audio_pb_decode_field_48fbe4(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_encode_field_490b1e(void*a,void*b){(void)a;(void)b;return 0;} void audio_uart_buffer_zero(void*a,unsigned n,unsigned c){unsigned char*p=a;for(unsigned i=0;i<n;i++)p[i]=(unsigned char)c;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_extension_unknown_48fc88',str(S/'display_pb_decode_extensions.c'),str(S/'display_pb_default_extension.c'),str(S/'display_pb_iter_begin_next.c'),str(S/'display_pb_iter_decode_advance.c'),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,tag,decode_ok):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;ext=0x20080100;typeptr=0x20080200;msg=0x20080300
  u.mem_write(stream,struct.pack('<IIII',0,0,10,0));u.mem_write(typeptr,struct.pack('<III',0,0,0x7766dc));u.mem_write(ext,struct.pack('<IIII',typeptr,msg,0,0));u.mem_write(msg,bytes(256));calls=[]
  addr=sy['audio_pb_decode_field_48fbe4'] if is_c else 0x48fbe4
  def hook(uc,pc,n,user):
   calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
   uc.reg_write(UC_ARM_REG_R0,decode_ok);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,tag),(UC_ARM_REG_R2,2),(UC_ARM_REG_R3,ext),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_decode_extension_unknown_48fc88'] if is_c else 0x48fc88)|1,0x600000,count=5000)
  err=struct.unpack('<I',bytes(u.mem_read(stream+12,4)))[0];message=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(ext+12,4)),calls,message
 for tag,ok in [(1,1),(2,1),(1,0)]:
  a=run(False,tag,ok);b=run(True,tag,ok);assert a==b,(tag,ok,a,b)
print('PASS_PB_DECODE_EXTENSIONS_NATIVE 3')
