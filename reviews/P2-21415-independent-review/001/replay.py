from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x789fec,0x789ff8),(0x774bc4,0x774bdc),(0x774bdc,0x774bf4)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==60
o=b/'analysis/review-isolated-P2-21415/fresh';o.mkdir(parents=True,exist_ok=False)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# Three copied configuration flash records\n\nPartial/unaccepted;60 exact non-code bytes in three record intervals. 789FEC..789FF8 three little-endianwords01000100,01000000,00000000;loadedbyLDMandcopiedSP0/4/8in21796before4D450C. 774BC4..774BDC sixwords00000006,2013BE70,00010100,20208E6F,00000000,00000001;copied24BtoSP36before4D4596. 774BDC..774BF4 sixwords00000007,20378D9C,00010100,2037919B,00000000,00000001;copied24BtoSP12before4D4596. Exactrawbytesauthoritative, nofieldtypesorRAMinitialcontentsassumed. Sourceslinkedthroughliterals484344/348/34C. Recordsremainsemanticallypartialpendinghelpercontracts; no C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=60,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',60)
