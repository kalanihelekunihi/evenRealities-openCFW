#!/usr/bin/env python3
"""Connected original/C nanopb decoding using authenticated dashboard descriptors."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
S=[p for p in sorted(D.glob('display_pb*.c')) if p.name!='display_pb_ostream_buffer.c']+[D/'display_uart_dashboard_pb_descriptor.c']
SHIM='''#include <stdint.h>
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){uint8_t *b=p;for(uint32_t i=0;i<n;i++)b[i]=(uint8_t)v;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_pb_decode',*[str(p) for p in S],str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,payload):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for addr,data in seg:u.mem_write(addr,data)
  stream=0x20080000;buf=0x20080100;msg=0x20081000
  u.mem_write(buf,payload or b'\0');u.mem_write(msg,b'\xaa'*188)
  cb=sy['audio_pb_buffer_read_48f3a4'] if is_c else 0x48f3a5
  u.mem_write(stream,struct.pack('<IIII',cb,buf,len(payload),0))
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,sy['audio_uart_dashboard_pb_descriptor'] if is_c else 0x776574),(UC_ARM_REG_R2,msg),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_uart_pb_decode'] if is_c else 0x490120)|1,0x600000,count=100000)
  s=bytes(u.mem_read(stream,16));err=struct.unpack_from('<I',s,12)[0]
  message=bytes(u.mem_read(err,48)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(msg,188)),s[4:12],message
 cases=[b'',b'\x18\x01',b'\x20\x96\x01',b'\x0a\x03abc',b'\x12\x03abc',b'\x30\x01',b'\x3a\0',b'\x40\x01',b'\0',b'\x80']
 for payload in cases:
  a=run(False,payload);b=run(True,payload)
  assert a==b,(payload,a,b)
print('PASS_UART_DASHBOARD_PB_DECODE_CONNECTED_NATIVE',len(cases))
