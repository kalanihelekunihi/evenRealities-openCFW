#!/usr/bin/env python3
"""Connected native/C default reset over authenticated ring descriptors."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
STUB='unsigned audio_pb_extension_iter_4d93a4(void*a,const void*b){(void)a;(void)b;return 0;} unsigned audio_pb_read_tag_48f66c(void*a,void*b,void*c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;} unsigned audio_pb_decode_field_48fbe4(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;} void audio_uart_pb_stream_init(void*a,const void*b,unsigned c){(void)a;(void)b;(void)c;} void audio_uart_buffer_zero(void*a,unsigned n,unsigned c){unsigned char*p=a;for(unsigned i=0;i<n;i++)p[i]=(unsigned char)c;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_default_fields_48fdf2',str(S/'display_pb_decode_defaults.c'),str(S/'display_pb_iter_begin_next.c'),str(S/'display_pb_iter_decode_advance.c'),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,desc,size):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  it=0x20080000;msg=0x20080100;u.mem_write(it,bytes(40));u.mem_write(msg,b'\xaa'*size)
  for reg,val in ((UC_ARM_REG_R0,it),(UC_ARM_REG_R1,desc),(UC_ARM_REG_R2,msg),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_iter_begin_4d94ba'] if is_c else 0x4d9384)|1,0x600000,count=1000)
  u.reg_write(UC_ARM_REG_R0,it);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_pb_default_fields_48fdf2'] if is_c else 0x48fdf2)|1,0x600000,count=10000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(it,40)),bytes(u.mem_read(msg,size))
 cases=[(0x7766dc,256),(0x7766f4,256),(0x77670c,256)]
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
print('PASS_PB_DEFAULT_FIELDS_CONNECTED_NATIVE',len(cases))
