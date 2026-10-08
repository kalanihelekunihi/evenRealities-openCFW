from pathlib import Path
import json,hashlib
b=Path('g2/build/pseudocode-first/20260930T190500Z');d=(b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
ranges=[(0x4849a4,0x4849fc)]
rows=[dict(start=a,end=z,bytes=d[a-0x438000:z-0x438000].hex()) for a,z in ranges]
assert sum(z-a for a,z in ranges)==88
o=b/'analysis/review-isolated-P2-21459/fresh';o.mkdir(parents=True,exist_ok=False)
(o/'bytes.json').write_text(json.dumps(rows,indent=2)+'\n')
(o/'pseudocode.md').write_text('# Dispatch and cleanup literal pool\n\nPartial/unaccepted. Exact 88 bytes at 0x4849A4..0x4849FC, decoded as 22 little-endian words.\n\n- 0x4849A4: 0x2006F690\n- 0x4849A8: 0x2006F548\n- 0x4849AC: 0x007865F0\n- 0x4849B0: 0x0077FBE4\n- 0x4849B4: 0x00760A70\n- 0x4849B8: 0x0077FBD0\n- 0x4849BC: 0x006E859C\n- 0x4849C0: 0x0077FC0C\n- 0x4849C4: 0x0077FBF8\n- 0x4849C8: 0x2006F684\n- 0x4849CC: 0x0073F4D0\n- 0x4849D0: 0x00760A90\n- 0x4849D4: 0x00786620\n- 0x4849D8: 0x00786610\n- 0x4849DC: 0x00786600\n- 0x4849E0: 0x00786630\n- 0x4849E4: 0x0077FC20\n- 0x4849E8: 0x007780BC\n- 0x4849EC: 0x0073F4FC\n- 0x4849F0: 0x007780D4\n- 0x4849F4: 0x0074A834\n- 0x4849F8: 0x00786640\n\nRAM addresses are runtime references; their ownership is unresolved. Consumers are recorded in maps 21818 through 21856. The global at 0x2006F548 supplies list heads and counters; 0x2006F684 supplies the reentrancy guard. Flash pointers used by diagnostics require separate pointed-data recovery. No C implementation, corpus freeze, whole-artifact coverage, or byte-equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),data_bytes=88,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',88)
