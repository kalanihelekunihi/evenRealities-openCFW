from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');a=b/'analysis';d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ids=[(16260,'001'),(15354,'001'),(16182,'001'),(16184,'001'),(16186,'001'),(16188,'002'),(16252,'001'),(16256,'001')];rows=[];sources=[]
for n,v in ids:
 matches=list(a.glob(f'*-{n}-map/{v}'));assert len(matches)==1,(n,matches)
 p=matches[0];blocks=json.loads((p/'instructions.json').read_text());rr=[r for block in blocks for r in block['instructions']];rows.extend(rr);sources.append(dict(path=str(p),files={f.name:h(f.read_bytes()) for f in p.iterdir() if f.is_file()}))
rows.sort(key=lambda r:r['address']);cursor=0x4d38ea
for r in rows:
 raw=bytes.fromhex(r['bytes']);assert r['address']==cursor and d[cursor-0x438000:cursor-0x438000+len(raw)]==raw;cursor+=len(raw)
assert cursor==0x4d39f2
boundaries={r['address'] for r in rows};edges=[]
for r in rows:
 if r['mnemonic'].startswith('b') and r['mnemonic'] not in ('bic','bic.w','bics','bics.w','bx'):
  m=re.match(r'([0-9a-f]{6,8})\b',r['operands'])
  if m:
   target=int(m[1],16);internal=0x4d38ea<=target<0x4d39f2
   assert not internal or target in boundaries,(r,target)
   edges.append(dict(source=r['address'],target=target,internal=internal,mnemonic=r['mnemonic']))
o=Path('reviews/P2-15859-clock-primitives-cluster-audit-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'sources.json').write_text(json.dumps(sources,indent=2)+'\n');(o/'edges.json').write_text(json.dumps(edges,indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),start=0x4d38ea,end=cursor,instruction_bytes=cursor-0x4d38ea,instructions=len(rows),maps=len(ids),edges=len(edges),external_targets=sorted({e['target'] for e in edges if not e['internal']}),checks=['Gap-free nonoverlapping byte-exact map partition','Every internal branch destination is instruction boundary','Corrected clock wait register16188 revision002 selected'],limitations=['Does not establish entry reachability all indirect edges semantics global ownership or complete firmware coverage','Adjacent padding and literal table beyond4D39F2 not part of code partition','No C admission freeze gates']),indent=2)+'\n');print('PASS',cursor-0x4d38ea,len(rows),len(edges))
