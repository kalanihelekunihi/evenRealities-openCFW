from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x47e084,0x47e088,b'tp_\0'),(0x47e140,0x47e144,b'rb\0\0'),(0x47e174,0x47e178,b'wb\0\0')];cons=[]
for n in (21334,21336,21338,21340):
 ps=list((b/'analysis').glob('*'+str(n)+'-map/001'));assert len(ps)==1;p=ps[0];r=json.loads((p/'receipt.json').read_text())
 for name,sha in r['files'].items():assert h((p/name).read_bytes())==sha
 for g in json.loads((p/'instructions.json').read_text()):
  for row in g['instructions']:
   m=re.search(r'adr r[0-9]+, ([0-9a-f]{6,8})',row['operands'])
   if m and int(m[1],16) in {a for a,z,v in ranges}:cons.append(dict(component=str(p),instruction=row,data_address=int(m[1],16)))
assert {x['data_address'] for x in cons}=={a for a,z,v in ranges}
for a,z,v in ranges:assert d[a-0x438000:z-0x438000]==v
o=b/'analysis/review-isolated-P2-20945/fresh';o.mkdir(parents=True,exist_ok=True)
(o/'data.json').write_text(json.dumps(dict(ranges=[dict(start=a,end=z,bytes=v.hex()) for a,z,v in ranges],consumers=cons),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted: three disjoint four-byte address-taken inline byte strings, total12bytes: E084 tp_ plus NUL; E140 rb plus two zero bytes; E174 wb plus two zero bytes. Four mapped ADR consumers verified against component hashes. String decoding does not prove external API meaning, ownership, other consumers or intervening padding classification. No C/freeze/completeness claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=12,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',12,len(cons))
