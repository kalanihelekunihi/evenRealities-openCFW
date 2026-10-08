from pathlib import Path
import json,hashlib,re
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x48173c;end=0x481818
cons=[]
for n in range(21558,21590,2):
 ps=list((b/'analysis').glob('*'+str(n)+'-map/001'))
 if not ps:continue
 assert len(ps)==1;p=ps[0];r=json.loads((p/'receipt.json').read_text())
 for name,sha in r['files'].items():assert h((p/name).read_bytes())==sha
 for g in json.loads((p/'instructions.json').read_text()):
  for row in g['instructions']:
   m=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])
   if m and ('pc' in row['operands']) and start<=int(m[1],16)<end:cons.append(dict(component=str(p),instruction=row,literal_address=int(m[1],16)))
assert {r['literal_address'] for r in cons}==set(range(start,end,4))
o=b/'analysis/apollo-main-diagnostic-fixed-library-indexed-bank-callback-fifty-five-word-literal-pool-21590-data/001';o.mkdir(parents=True,exist_ok=False)
(o/'data.json').write_text(json.dumps(dict(start=start,end=end,bytes=d[start-0x438000:end-0x438000].hex(),words=[dict(address=a,value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in range(start,end,4)],consumers=cons),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted:220 bytes48173C..481818;55 aligned literal words with decoded PC-relative LDR consumers across maps21558..21588. Exact raw words and consumers preserved in data.json; source component receipts checked. Every literal slot has a decoded consumer. Table pointers, bank register pointers, callback/argument arrays and scalar values are recorded without inferring pointed ownership or implementing C. Pointed table/array contents and any external hardware semantics remain separate recovery requirements. No freeze/fullcoverage/source/equality claim.\n')

(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),files={p.name:h(p.read_bytes()) for p in o.iterdir() if p.name!='receipt.json'}),indent=2)+'\n');print('PASS',end-start,len(cons))
