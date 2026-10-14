from pathlib import Path
import json,struct,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];B=H.parent;F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';raw=F.read_bytes()[32:]
roots=json.loads((B/'case-wave025-ram-callback-provenance/verification.json').read_text())['known_roots'];cat=list(map(json.loads,(R/'g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines()))
# Half-open code and literal spans, individually reviewed against locked bytes,
# exact branch terminals/backedges and existing source providers. Never scan pools.
spec={0xb8:(0xc4,[(0xc4,0xcc)]),0x8558:(0x856c,[]),0xa380:(0xa392,[(0xa394,0xa39c)]),0xae5c:(0xae6e,[(0xae70,0xae74)]),0xb31c:(0xb32c,[(0xb32c,0xb330)]),0xb360:(0xb374,[]),0xbf84:(0xbf8c,[]),0xbf8c:(0xbf94,[])}
missing={int(x['native'],16)-0x8000000:x for x in roots if not any(int(f['body_start'],16)<=int(x['native'],16)<=int(f['body_end_inclusive'],16) for f in cat)};assert set(missing)==set(spec)
rows=[];new=[];previous={int(x['PC'],16) for x in json.loads((B/'case-wave055-ram-stack-evidence-review/verification.json').read_text())['indirect_control_candidates']}
for start,(end,pools) in spec.items():
 pc=start;instructions=[];literal=[];sites=[]
 while pc<end:
  w=struct.unpack_from('<H',raw,pc)[0];width=4 if w>>11 in [0b11101,0b11110,0b11111] else 2;assert pc+width<=end
  if w&0xf800==0x4800:
   address=((pc+4)&~3)+(w&255)*4;assert any(a<=address and address+4<=b for a,b in pools)
   literal.append(dict(PC=hex(0x8000000+pc),literal_address=hex(0x8000000+address),value=hex(struct.unpack_from('<I',raw,address)[0])))
  if w&0xff87 in [0x4700,0x4780] and not (w&0xff87==0x4700 and (w>>3)&15==14):
   s=dict(PC=hex(0x8000000+pc),opcode=hex(w),kind='BLX' if w&128 else 'BX',register=(w>>3)&15,previously_catalogue_scanned=0x8000000+pc in previous);sites.append(s)
   if not s['previously_catalogue_scanned']:new.append(s)
  instructions.append(dict(PC=hex(0x8000000+pc),width=width,bytes=raw[pc:pc+width].hex()));pc+=width
 rows.append(dict(native_entry=hex(0x8000000+start),source_symbol=missing[start]['source_symbol'],code_span=[hex(0x8000000+start),hex(0x8000000+end)],code_sha256=hashlib.sha256(raw[start:end]).hexdigest(),literal_spans=[[hex(0x8000000+a),hex(0x8000000+b)] for a,b in pools],literal_loads=literal,instructions=instructions,indirect_sites=sites))
assert len(new)==1 and new[0]['PC']=='0x8008568'
r=dict(status='PASS_8_OMITTED_KNOWN_ROOT_CODE_DATA_REVIEWS',known_roots=39,omitted_root_entries=8,reviewed_roots=rows,new_indirect_sites=new,corrected_candidate_count=24,limits=['Known39 roots supplemented only, not all possible indirect targets or full corpus CFG closure','Byte width and literal-pool references checked mechanically; extents reviewed by producer, independent reviewer acceptance not claimed','Startup BX080000c2 already present under overlapping catalogue veneer; only timer BLX08008568 adds a unique site','No execution stack or physical hardware inference from static boundaries'])
(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],new)
