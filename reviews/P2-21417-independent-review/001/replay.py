from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x75165c,0x75167f),(0x75d650,0x75d66d)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==64
o=b/'analysis/review-isolated-P2-21417/fresh';o.mkdir(parents=True,exist_ok=False)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# TLSF pool and mutex failure diagnostic strings\n\nPartial/unaccepted;64 exactdata bytes in two NUL-terminated strings. 75165C..75167F ASCII TLSF memory pool creation failed! followednewline0AandNUL00 (35B). 75D650..75D66D ASCII TLSF mutex creation failed! followednewline0AandNUL00 (29B). Literals484360/484364pointrespectivelyhere;map21798passesfirstto4733EEwhen4D06ECreturnsnull andsecondwhen4416D6returnsnull,thenobservedselfloops. StringsprovideauthoritativeTLSFpool/mutexnamingevidence; fullhelpercontractsremainseparate. No bytesafterNULclaimed,paddingownershippending. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=64,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',64)
