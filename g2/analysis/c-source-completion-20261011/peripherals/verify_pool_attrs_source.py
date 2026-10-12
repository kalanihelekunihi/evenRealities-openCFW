#!/usr/bin/env python3
"""Qualify source-owned CMSIS pool attributes against native data records."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/pool_attrs_data.c'
def words(a,n):return struct.unpack_from('<'+'I'*n,B,a-0x438000)
q=words(0x77ccac,6);t=words(0x75bd00,9)
assert q==(0x784388,0,0x20072e98,0x50,0x203737c0,0xbb8)
assert t==(0,0,0,0,0,0x1000,0x2b,0,0)
assert B[0x784388-0x438000:].split(b'\0')[0]==b'threadpool_Queue'
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'attrs.o'
 subprocess.run(['clang','--target=armv8.1m.main-none-eabi','-mcpu=cortex-m55','-mthumb','-mfloat-abi=hard','-mfpu=fpv5-sp-d16','-std=c11','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(obj)],check=True)
 with obj.open('rb') as f:
  e=ELFFile(f);sym=e.get_section_by_name('.symtab');sy={v.name:v for v in sym.iter_symbols()}
  a=sy['audio_uart_pool_queue_attrs'];b=sy['audio_uart_pool_thread_attrs']
  assert a['st_size']==24 and b['st_size']==36
  ro=e.get_section(a['st_shndx']);data=ro.data()
  av=data[a['st_value']:a['st_value']+24];bv=data[b['st_value']:b['st_value']+36]
  assert struct.unpack_from('<I',av,4)[0]==0
  assert struct.unpack_from('<I',av,12)[0]==0x50
  assert struct.unpack_from('<I',av,20)[0]==0xbb8
  assert struct.unpack_from('<9I',bv)==t
  rel=e.get_section_by_name('.rel.rodata');rels={v['r_offset']-a['st_value']:sym.get_symbol(v['r_info_sym']).name for v in rel.iter_relocations() if a['st_value']<=v['r_offset']<a['st_value']+24}
  assert len(rels)==3 and rels[8]=='audio_uart_pool_queue_control_mem' and rels[16]=='audio_uart_pool_queue_storage',rels
print('PASS_POOL_ATTRS_SOURCE',2,'records',3,'relocations')
