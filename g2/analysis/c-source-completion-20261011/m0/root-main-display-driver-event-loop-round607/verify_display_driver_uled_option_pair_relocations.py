#!/usr/bin/env python3
"""Check two C callback relocations and unchanged native option words."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
here=Path(__file__).resolve().parent
root=here.parents[3]
official=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
object_file=root/'build/c-firmware/root-main-display-driver-relocated-pair-round682/display_driver_uled_options_relocated_pair.o'
with object_file.open('rb') as file:
 elf=ELFFile(file)
 data=elf.get_section_by_name('.rodata').data()
 symbols=elf.get_section_by_name('.symtab')
 reloc=elf.get_section_by_name('.rel.rodata')
 observed={entry['r_offset']:symbols.get_symbol(entry['r_info_sym']).name for entry in reloc.iter_relocations()}
 assert observed=={
  0:'display_driver_uled_option_type1_irq_5bbd48',
  64:'display_driver_uled_option_type0_irq_592658'},observed
 for offset,native in ((0,0x70afe4),(64,0x70b024)):
  source_words=[int.from_bytes(data[offset+4*i:offset+4*i+4],'little') for i in range(16)]
  original_offset=native-0x438000+32
  original_words=[int.from_bytes(official[original_offset+4*i:original_offset+4*i+4],'little') for i in range(16)]
  assert source_words[0]==0
  assert source_words[1:]==original_words[1:],(hex(native),source_words,original_words)
integrated=root/'build/c-firmware/root-main-uled-option-pair-integration-round682/candidate.o'
with integrated.open('rb') as file:
 elf=ELFFile(file)
 symbols=elf.get_section_by_name('.symtab')
 by_name={symbol.name:symbol for symbol in symbols.iter_symbols()}
 relocations=[]
 for section in elf.iter_sections():
  if section['sh_type']!='SHT_REL':continue
  for entry in section.iter_relocations():
   symbol=symbols.get_symbol(entry['r_info_sym'])
   if symbol.name in observed.values():
    assert symbol['st_value']&1,symbol.name
    relocations.append((entry['r_offset'],symbol.name))
 assert sorted(relocations)==sorted((by_name[table]['st_value']+offset,callback)
   for table,offset,callback in (
    ('display_driver_uled_option_type1',0,'display_driver_uled_option_type1_irq_5bbd48'),
    ('display_driver_uled_option_type0',0,'display_driver_uled_option_type0_irq_592658'))),relocations
 print('PASS_ULED_OPTION_PAIR_RELOCATIONS',len(observed),'native_words_preserved',30)
