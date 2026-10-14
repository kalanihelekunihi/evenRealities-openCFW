#!/usr/bin/env python3
"""Compare compiled NEMA mode lookups with official flash records."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
source=Path(__file__).with_name('display_driver_nema_mode_tables.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
records={'display_driver_nema_mode_format_a':(0x6df0f4,48),
         'display_driver_nema_mode_format_b':(0x6df124,48),
         'display_driver_nema_mode_format_b_tail':(0x6df154,16),
         'display_driver_nema_mode_target_bits':(0x513ec0,16)}
with tempfile.TemporaryDirectory() as directory:
 obj=Path(directory)/'tables.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55',
                 '-mthumb','-std=c11','-ffreestanding','-fno-builtin',
                 '-Wall','-Wextra','-Werror','-O2','-c',str(source),'-o',str(obj)],
                check=True)
 with obj.open('rb') as file:
  elf=ELFFile(file)
  symbols={symbol.name:symbol for symbol in
           elf.get_section_by_name('.symtab').iter_symbols()}
  for name,(address,size) in records.items():
   symbol=symbols[name]
   assert symbol['st_size']==size,(name,symbol['st_size'])
   section=elf.get_section(symbol['st_shndx'])
   offset=symbol['st_value']-section['sh_addr']
   candidate=section.data()[offset:offset+size]
   native=blob[address-0x438000:address-0x438000+size]
   assert candidate==native,(name,candidate.hex(),native.hex())
print('PASS_DISPLAY_DRIVER_NEMA_MODE_TABLES_EXACT 4 128')
