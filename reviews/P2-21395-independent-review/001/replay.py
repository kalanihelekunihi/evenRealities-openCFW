from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x4840aa,0x4840ac),(0x4840c6,0x4840c8)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==4
o=b/'analysis/review-isolated-P2-21395/fresh';o.mkdir(parents=True,exist_ok=False)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# Registration helper and callback alignment halfwords\n\nPartial/unaccepted;four exact non-code bytes. 4840AA..4840AC is zero halfword after traversal return21790 and before callback4840AC. 4840C6..4840C8 is zero halfword after callback return21792 and before nextentry4840C8. Exact bytes.json authoritative. No executable behavior assigned to these padding slots; branch/reference ownership beyondlocaladjacency remains subject to whole-artifact audit. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=4,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',4)
