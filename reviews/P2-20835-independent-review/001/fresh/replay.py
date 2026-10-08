from pathlib import Path
import hashlib,json,struct
b=Path('g2/build/pseudocode-first/20260930T190500Z');h=lambda x:hashlib.sha256(x).hexdigest();d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
p=b/'analysis/apollo-main-diagnostic-fixed-library-byte-table-high-byte-xor-rolling-word-update-21228-map/001';r=json.loads((p/'receipt.json').read_text())
for name,sha in r['files'].items():assert h((p/name).read_bytes())==sha
start=struct.unpack_from('<I',d,0x47cc14-0x438000)[0];assert start==0x6983a8;end=start+1024;raw=d[start-0x438000:end-0x438000];words=list(struct.unpack('<256I',raw));poly=0x1edc6f41
expected=[]
for i in range(256):
 v=i<<24
 for _ in range(8):v=((v<<1)^ (poly if v&0x80000000 else 0))&0xffffffff
 expected.append(v)
assert words==expected
# Index is an unsigned byte XOR a logical top byte, hence exactly 0..255.
o=b/'analysis/review-isolated-P2-20835/fresh';o.mkdir(parents=True,exist_ok=True)
(o/'data.json').write_text(json.dumps(dict(start=start,end=end,bytes=raw.hex(),words=words,pointer_literal=0x47cc14,consumer_component=str(p),consumer_receipt_sha256=h((p/'receipt.json').read_bytes()),index_bounds=[0,255],recurrence_polynomial=poly),indent=2)+'\n')
(o/'REPORT.md').write_text('Partial/unaccepted: exact 1024 bytes at 0x6983A8..0x6987A8; 256 little-endian words. Pinned literal47CC14 points to this table. Mapped helper index is byte XOR state logical top byte, bounded0..255. Every entry matches eight MSB-first shift/XOR steps from index<<24 using0x1EDC6F41; this is verified recurrence, not an inferred external protocol contract. Other consumers, broader data ownership and whole-corpus completeness remain unproven. No C/freeze changes.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),files={x.name:h(x.read_bytes()) for x in o.iterdir()}),indent=2)+'\n');print('PASS',len(raw),len(words),hex(poly))
