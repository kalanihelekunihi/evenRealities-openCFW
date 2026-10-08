from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
rows=[];components=[];cursor=0x47aed4;end=0x47b3ae
for n in range(21104,21130,2):
 matches=list((b/'analysis').glob('*'+str(n)+'-map/001'));assert len(matches)==1;p=matches[0];r=json.loads((p/'receipt.json').read_text());assert r['input_sha256']==h(d)
 for name,sha in r['files'].items():assert h((p/name).read_bytes())==sha
 groups=json.loads((p/'instructions.json').read_text());components.append(dict(path=str(p),receipt_sha256=h((p/'receipt.json').read_bytes())))
 for g in groups:
  for row in g['instructions']:
   a=row['address'];raw=bytes.fromhex(row['bytes']);assert a==cursor and raw==d[a-0x438000:a-0x438000+len(raw)];cursor+=len(raw);rows.append(row)
assert cursor==end
starts={r['address'] for r in rows};branches=[]
for r in rows:
 m=r['mnemonic'];target=re.match(r'([0-9a-f]{6,8})\s*<',r['operands'])
 if m.startswith('b') and m not in ('bl','blx','bic','bics','bkpt','bx') and target:
  a=int(target[1],16)
  if 0x47aed4<=a<end:assert a in starts;branches.append(dict(source=r['address'],target=a))
o=Path('reviews/P2-20729-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False)
(o/'continuity.json').write_text(json.dumps(dict(start=0x47aed4,end=end,instruction_bytes=end-0x47aed4,instruction_count=len(rows),local_branches=branches,components=components),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted continuity47AED4..47B3AE,1242instruction bytes,thirteen maps. Component hashes,pinned tiling andlocalbranchboundaries checked. Four selector routes, ordered record writes, separate diagnostic reads and88-byte frame shared live return retained. No source/freeze/wholefirmwareclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',cursor-0x47aed4,len(rows),len(branches))
