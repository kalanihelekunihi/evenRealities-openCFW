from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47b4ac;end=0x47b4c8
cons=[]
for n in range(20846,21140,2):
 ps=list((b/'analysis').glob('*'+str(n)+'-map/001'))
 if not ps:continue
 assert len(ps)==1;p=ps[0];r=json.loads((p/'receipt.json').read_text())
 for name,sha in r['files'].items():assert h((p/name).read_bytes())==sha
 for g in json.loads((p/'instructions.json').read_text()):
  for row in g['instructions']:
   m=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])
   if m and 'pc' in row['operands'] and start<=int(m[1],16)<end:cons.append(dict(component=str(p),instruction=row,literal_address=int(m[1],16)))
assert {r['literal_address'] for r in cons}==set(range(start,end,4))
o=Path('reviews/P2-20739-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False)
(o/'data.json').write_text(json.dumps(dict(start=start,end=end,bytes=d[start-0x438000:end-0x438000].hex(),words=[dict(address=a,value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in range(start,end,4)],consumers=cons),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted:28 bytes,seven aligned little-endian literal words47B4AC..47B4C8. Every word has mapped PC-load consumers retained with raw instructions and component hash checks. Pointed-to ownership and whole corpus coverage unproven; no source/freeze changes.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start,len(cons))
