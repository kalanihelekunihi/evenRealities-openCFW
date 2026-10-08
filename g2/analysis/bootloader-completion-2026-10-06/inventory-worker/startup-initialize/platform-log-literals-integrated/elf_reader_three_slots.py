# SPDX-License-Identifier: MIT
"""Strict bounded ARM32 ELF reader for source-only bootloader test modules."""
from elftools.elf.elffile import ELFFile
from pathlib import Path
def elf_info(path):
 p=Path(path);assert p.stat().st_size<=2*1024*1024
 with p.open('rb') as f:
  elf=ELFFile(f);assert elf.elfclass==32 and elf.little_endian and elf['e_machine']=='EM_ARM' and elf['e_type']=='ET_EXEC'
  segments=[]
  for s in elf.iter_segments():
   if s['p_type']!='PT_LOAD':continue
   lo=s['p_vaddr'];size=s['p_memsz'];assert s['p_filesz']<=size<=65536
   # Three explicit relocated source slots, each still bounded to64KiB.
   assert any(a<=lo<=lo+size<=b for a,b in [(0x10000,0x20000),(0x30000,0x40000),(0x50000,0x60000),(0x410000,0x434477),(0x20000000,0x20040000)])
   segments.append(dict(address=lo,memory_size=size,data=s.data(),flags=s['p_flags']))
  section=elf.get_section_by_name('.symtab');assert section
  symbols={s.name:s['st_value'] for s in section.iter_symbols() if s.name and s['st_shndx']!='SHN_UNDEF'}
 return p.read_bytes(),segments,symbols
