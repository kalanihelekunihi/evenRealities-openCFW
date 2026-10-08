from pathlib import Path
import hashlib,json,struct
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
components=[];templates=[]
for n,lit,addr,raw in [(21362,0x47e614,0x78b648,'010000000000000000000000')]:
 ps=list((b/'analysis').glob('*'+str(n)+'-map/001'));assert len(ps)==1;p=ps[0];r=json.loads((p/'receipt.json').read_text());assert r['input_sha256']==h(d)
 for name,sha in r['files'].items():assert h((p/name).read_bytes())==sha
 assert struct.unpack_from('<I',d,lit-0x438000)[0]==addr
 actual=d[addr-0x438000:addr-0x438000+12];assert actual.hex()==raw
 templates.append(dict(pointer_literal=lit,start=addr,end=addr+12,bytes=raw,consumer=str(p),consumer_receipt_sha256=h((p/'receipt.json').read_bytes())))
start=0x78b648;end=0x78b654;assert len(d[start-0x438000:end-0x438000])==12
o=b/'analysis/apollo-main-diagnostic-fixed-library-low-byte-request-twelve-byte-template-21366-data/001';o.mkdir(parents=True,exist_ok=False)
(o/'data.json').write_text(json.dumps(dict(start=start,end=end,bytes=d[start-0x438000:end-0x438000].hex(),templates=templates),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted:12exactbytes78B648..78B654,threewords1/0/0. Pointer47E614andmap21362componenthashverified. Consumerloadsallthreewords thenoverwritesmiddlestackwordwithLOW8entryR0. Pointedownership/otherconsumersunproven. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),files={x.name:h(x.read_bytes()) for x in o.iterdir()}),indent=2)+'\n');print('PASS',end-start,len(templates))
