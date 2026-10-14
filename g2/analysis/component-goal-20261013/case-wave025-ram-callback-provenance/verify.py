#!/usr/bin/env python3
"""Bounded source literal, known-root and immutable string provenance audit."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
import re,json,hashlib,struct,ast,collections
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave022-logging-stack';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:{'path':str(p.relative_to(R)),'sha256':sha(p)}
inv=P/'final/receipt.json';d=json.loads(inv.read_text());F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';b=F.read_bytes()[32:];E=P/'final/case.elf'
assert sha(F)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with E.open('rb') as f:
 e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
a=collections.defaultdict(list)
for row in d['sources']:
 p=R/row['source'];assert sha(p)==row['source_sha256'];s=re.sub(r'/\*.*?\*/|//[^\n]*','',p.read_text(),flags=re.S)
 for m in re.finditer(r'0x(200[0-9a-fA-F]{5})[uUlL]*',s):a[int(m[1],16)].append(row['source'])
ram=[]
for addr,files in sorted(a.items()):
 packed=struct.pack('<I',addr);offsets=[hex(0x08000000+i) for i in range(0,len(b)-3,4) if b[i:i+4]==packed]
 ram.append({'address':hex(addr),'source_files':sorted(set(files)),'aligned_native_literal_word_locations':offsets,'evidence_status':'native_literal_word_present_not_object_extent_proof' if offsets else 'derived_address_requires_native_base_plus_offset_join'})
assert all(int(x['address'],16)<=0x20002c88 for x in ram)
rootsfile=R/'g2/analysis/c-source-completion-20261011/m0/case_semantic_corrected_optimized.indirect-roots.json';roots=json.loads(rootsfile.read_text());joined=[]
for row in roots['rows']:
 n=row['source_symbol'];assert n in symbols;addr=int(row['native'],16);target=struct.pack('<I',addr|1);offsets=[hex(0x08000000+i) for i in range(0,len(b)-3,4) if b[i:i+4]==target];joined.append({'native':row['native'],'source_symbol':n,'current_linked_address':hex(symbols[n]),'aligned_native_thumb_pointer_locations':offsets,'limits':'Known target identity joined only; computed pointers, registration lifetime and all callbacks not proven'})
stringsfile=R/'g2/components/case/semantic_strings_candidate_20261011/case_semantic_strings.c';strings=[]
for m in re.finditer(r'const char case_string_([0-9a-f]{8})\[\] = ("(?:[^"\\]|\\.)*");',stringsfile.read_text()):
 address=int(m[1],16);value=ast.literal_eval(m[2]).encode('latin1')+b'\0';offset=address-0x08000000;assert b[offset:offset+len(value)]==value,(m[1],value);strings.append({'native_address':hex(address),'source_symbol':'case_string_'+m[1],'bytes_including_NUL':len(value),'sha256':hashlib.sha256(value).hexdigest()})
assert len(strings)>100
r={'status':'PASS_BOUNDED_LITERAL_ROOT_STRING_PROVENANCE_AUDIT','input_inventory':ref(inv),'ELF':ref(E),'firmware':ref(F),'source_units':len(d['sources']),'RAM_literal_count':len(ram),'RAM_literals':ram,'native_literal_word_present_count':sum(bool(x['aligned_native_literal_word_locations']) for x in ram),'derived_address_join_pending_count':sum(not x['aligned_native_literal_word_locations'] for x in ram),'known_root_count':len(joined),'known_roots':joined,'root_inventory':ref(rootsfile),'exact_native_string_count':len(strings),'strings':strings,'string_source':ref(stringsfile),'limits':['Lexical literals within authenticated initialized RAM/SP envelope do not prove computed offsets, access widths, object extents, memory lifetime or physical SRAM capacity.','Native word occurrence is provenance evidence only; no code/data classification or coverage interval promotion.','Known39 root set is inherited, not a complete callback discovery proof.','String bytes agree with native addresses; caller interior offsets and argument contracts still require per-call evidence.']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['RAM_literal_count'],r['derived_address_join_pending_count'],r['known_root_count'],r['exact_native_string_count'])
