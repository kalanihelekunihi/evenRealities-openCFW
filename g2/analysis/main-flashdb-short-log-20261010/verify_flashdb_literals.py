#!/usr/bin/env python3
"""Compare source-owned FlashDB strings with authenticated stock literal targets."""
from pathlib import Path
import hashlib, json, struct, subprocess
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent
R=H.parents[2]
src=R/'g2/components/main/flashdb_literal_candidates_20261010/literals.c'
stock=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
b=stock.read_bytes()
assert hashlib.sha256(b).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
def stock_word(addr):return struct.unpack_from('<I',b,addr-0x437fe0)[0]
targets=[stock_word(a) for a in (0x5412c8,0x541268,0x541264,0x5412d0,0x5412cc,0x5412d4)]
assert targets==[0x2005dffc,0x78e54c,0x6e4cc8,0x783190,0x75996c,0x743150]
elf=H/'flashdb-literals.elf'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip()
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz',
     '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
     '-Wl,--defsym=g2_flashdb_db_rows=0x2005dffc',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True)
with elf.open('rb') as f:
 e=ELFFile(f)
 syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 chunks=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
 def read(addr,n):
  for base,data in chunks:
   if base<=addr and addr+n<=base+len(data):return data[addr-base:addr-base+n]
  raise AssertionError(hex(addr))
 table=struct.unpack('<7I',read(syms['g2_flashdb_candidate_literals'],28))
 assert table[0]==targets[0] and table[6]==0
 rows=[]
 for i in range(1,6):
  orig=b[targets[i]-0x437fe0:].split(b'\0',1)[0]
  compiled=read(table[i],len(orig)+1)
  assert compiled==orig+b'\0',(i,orig,compiled)
  rows.append({'index':i,'stock_address':hex(targets[i]),'source_address':hex(table[i]),
               'length_including_nul':len(compiled),'sha256':hashlib.sha256(compiled).hexdigest()})
result={'status':'PASS','strings':5,'table_words':7,'database_base_fixture':hex(table[0]),
        'rows':rows,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'compile':cmd,
        'limits':'Stock/source string bytes and semantic table slots only; DB object definition, address placement and producer linker order remain external.'}
(H/'literals-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(rows),'strings')
