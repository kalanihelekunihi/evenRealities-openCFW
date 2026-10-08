from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x484344,0x484380)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==60
o=b/'analysis/review-isolated-P2-21413/fresh';o.mkdir(parents=True,exist_ok=False)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# Configuration and resource fifteen-pointer literal pool\n\nPartial/unaccepted;60 exactdata bytes484344..484380,fifteenlittle-endianwords. Address:value pairs:\n484344:00789FEC;484348:00774BC4;48434C:00774BDC;\n484350:200007BC;484354:200007D4;484358:20000630;48435C:20000C20;\n484360:0075165C;484364:0075D650;\n484368:20279670;48436C:20000338;484370:20000354;484374:2013BE70;484378:20000370;48437C:20378D9C.\n\n21796consumesfirstseven:3wordflashrecord,2x24Bflashrecords andfourRAMpointers. 21798consumes484360/364diagnosticpointers. 21808/21810consume484368..37Cfor3objectinitializers(base/object pairs),andglobalwrappersreuse48436C. Values outsidelockedflash range are rawruntimeaddresses; no initialRAMcontentsorrecordtypesinvented. Pointedflashrecords/strings remain to recover. bytes.jsonauthoritative,no C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=60,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',60)
