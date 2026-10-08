from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x484010,0x484014),(0x6ee378,0x6ee3c8),(0x78dc7c,0x78dc8c)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==100
o=b/'analysis/review-isolated-P2-21387/fresh';o.mkdir(parents=True,exist_ok=False)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# Formatter reversed infinity strings, power-ten table and callback literal\n\nPartial/unaccepted;100 exact data bytes in three disjoint intervals. 484010..484014 little-endianword00483029 Thumb483028|1, callback used by wrappers21784. 78DC7C..78DC84 ASCII fni- thenNULandthreezeros;78DC84..78DC8C ASCII fni+ thenNULandthreezeros. Consumers21728/21730sendfirst4bytes through reverse-output48306C, yielding -inf/+inf; exactstoredorderretained.\n\n6EE378..6EE3C8 contains ten eight-byte little-endianbinary64 entries exactly1,10,100,1000,10000,100000,1000000,10000000,100000000,1000000000 inascendingindex0..9. Tablepointer484000→6EE378;consumer21732capsprecisionindexbelow10 thenreadsbase+8*R7;21734comparesroundcarryagainstthesameindex. Rawbitsauthoritative;all ten values exactlyrepresentable. No additionaltableextentclaimed; tableownershipbeyondcandidateunresolved. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=100,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',100)
