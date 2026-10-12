#!/usr/bin/env python3
"""Check source-owned ANCC nanopb records against authenticated stock ROM."""
from hashlib import sha256
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
R=Path(__file__).resolve().parents[3]
ota=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert sha256(ota).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
stock=ota[32:];base=0x438000
source=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_pb_descriptor.c'
field_addrs={'fields_7799f4':0x72b4d4,'fields_779a24':0x779a0c,'fields_779a54':0x779a3c,
             'fields_779a6c':0x78b5f4,'fields_779a84':0x78b600,'fields_779a9c':0x787ad0}
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'ancc.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2','-ffreestanding',
  '-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
 with obj.open('rb') as f:
  elf=ELFFile(f);sy={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
  count=0;total=0
  for name,addr in field_addrs.items():
   s=sy[name];section=elf.get_section(s['st_shndx']);data=section.data()[s['st_value']:s['st_value']+s['st_size']]
   assert data==stock[addr-base:addr-base+len(data)],(name,'field records')
   count+=1;total+=len(data)
  for name,addr in [('audio_ble_ancc_not_whitelisted_pb_descriptor',0x7799f4)]+[(f'desc_{a:06x}',a) for a in (0x779a24,0x779a54,0x779a6c,0x779a84,0x779a9c)]:
   s=sy[name];section=elf.get_section(s['st_shndx']);data=section.data()[s['st_value']:s['st_value']+s['st_size']]
   assert len(data)==24 and data[8:24]==stock[addr-base+8:addr-base+24],(name,'descriptor counts')
  assert count==6 and total==140,(count,total)
print('PASS_ANCC_PB_DESCRIPTOR_6_RECORDS_140_FIELD_BYTES')
