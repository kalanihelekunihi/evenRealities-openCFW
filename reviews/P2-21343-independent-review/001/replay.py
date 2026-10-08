from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x482ab2,0x482ab4),(0x482f72,0x482f74),(0x48334e,0x483350),(0x483612,0x48364c)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==64
o=b/'analysis/review-isolated-P2-21343/fresh';o.mkdir(parents=True,exist_ok=True)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# Floating literals, strings and library padding\n\nPartial/unaccepted; 64 exact data bytes in four intervals. Zero halfwords 482AB2..482AB4,482F72..482F74,48334E..483350 follow previously recovered returns. 483612..483614 is zero padding after floating formatter return. 483614 ASCII nan plus NUL;483628 ASCII fni plus NUL, deliberately retain byte order used by reverse-output helper.\n\nFull eight-byte little-endian binary64 literals:483618 FFFFFFFFFFFFEFFF = negative maximum finite;483620 000000000000F07F = positive infinity;48362C 0100000065CDCD41 = next representable value above 1000000000;483634 0000000065CDCDC1 = -1000000000;48363C 0000000000000000 = positive zero;483644 010000000000E03F = next representable value above 0.5. Exact bytes authoritative, including low-order one bits. These resolve full-width VLDR reads previously represented by four-byte reference prefixes in maps21728..21734. Candidate ends before code48364C. No C, freeze, whole coverage or equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=64,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',64)
