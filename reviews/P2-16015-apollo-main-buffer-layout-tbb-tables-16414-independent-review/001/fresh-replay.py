from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';tables=[]
for start,length,indexbias,consumer,targets in [(0x4b130c,68,11,0x4b1308,{0x4b1350,0x4b1356,0x4b135a,0x4b135e,0x4b1360,0x4b136c}),(0x4b1378,75,4,0x4b1374,{0x4b13c4,0x4b13c8,0x4b13cc,0x4b13ce})]:
 raw=d[start-0x438000:start-0x438000+length];rows=[]
 for i,v in enumerate(raw):
  target=start+2*v;assert target in targets,(hex(start),i,hex(target));rows.append(dict(index=i,format=i+indexbias,byte=v,target=target))
 tables.append(dict(address=start,length=length,bytes=raw.hex(),sha256=h(raw),consumer=consumer,semantics='TBB unsignedbyte offset doubled relative to consumerPC+4',rows=rows))
unused=d[0x4b13c3-0x438000:0x4b13c4-0x438000]
o=b/'reviews/P2-16015-apollo-main-buffer-layout-tbb-tables-16414-independent-review/001/fresh/outputs';o.mkdir(parents=True,exist_ok=False);(o/'tables.json').write_text(json.dumps(dict(status='partial',accepted=False,image_sha256=h(d),tables=tables,excluded_byte=dict(address=0x4b13c3,bytes=unused.hex(),classification='excluded from raw function ranges and bounded TBB index; not yet globally classified')),indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(status='partial',accepted=False,data_bytes=143,excluded_bytes=1,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS143 TBBbytes 1excludedbyte')
