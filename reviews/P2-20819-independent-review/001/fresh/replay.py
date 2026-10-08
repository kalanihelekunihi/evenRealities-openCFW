from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
rows=[];components=[];cursor=0x47c2bc;end=0x47c504
for n in range(21210,21218,2):
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
  if 0x47c2bc<=a<end:assert a in starts;branches.append(dict(source=r['address'],target=a))
o=b/'analysis/review-isolated-P2-20819/fresh';o.mkdir(parents=True,exist_ok=True)
(o/'continuity.json').write_text(json.dumps(dict(start=0x47c2bc,end=end,instruction_bytes=end-0x47c2bc,instruction_count=len(rows),local_branches=branches,components=components),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted continuity47C2BC..47C504,584instructionbytes,fourmaps. Component hashes,pinned rawbyte tiling andlocalbranchtargets checked.64frame,fourfreshguards,stride256,distincteligible/visitcounts,diagnosticorder andliveR0return preserved. No wholecoverage/source/freezeclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',cursor-0x47c2bc,len(rows),len(branches))
