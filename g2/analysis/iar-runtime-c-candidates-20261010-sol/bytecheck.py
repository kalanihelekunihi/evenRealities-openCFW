from pathlib import Path
import json
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
rows=json.loads((R/'g2/analysis/shortcut-iar-shortlist-review-20261010-daybreak/evidence.json').read_text())['reviewed']
names=['g2_isxdigit','g2_strcat','g2_strcspn','g2_strrchr','g2_strspn','g2_putchars','g2_getn','g2_ungetn','g2_ranmatch','g2_zero_init3']
stock=(R/'g2/build/pseudocode-first/20260930T190500Z/attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();out=[]
for filename in ['runtime.elf','runtime-m55.o']:
 with (D/filename).open('rb') as f:
  e=ELFFile(f);syms={s.name:s for s in e.get_section_by_name('.symtab').iter_symbols()}
  for row,name in zip(rows,names):
   s=syms[name];section=e.get_section(s['st_shndx']);offset=(s['st_value']&~1)-section['sh_addr'];b=section.data()[offset:offset+s['st_size']];a=int(row['runtime'],16)-0x438000;orig=stock[a:a+row['bytes']]
   out.append(dict(build=filename,name=name,original_bytes=len(orig),compiled_bytes=len(b),byte_equal=b==orig))
(D/'byte-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print('exact',sum(x['byte_equal'] for x in out),'/',len(out))
