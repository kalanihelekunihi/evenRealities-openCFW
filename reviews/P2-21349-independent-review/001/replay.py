from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x483798;end=0x483820
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'input.bin').write_bytes(d[start-0x438000:end-0x438000]);(t/'input.s').write_text('.syntax unified\n.cpu cortex-m55\n.thumb\n.text\n.incbin "'+str(t/'input.bin')+'"\n');subprocess.run(['/opt/homebrew/bin/arm-none-eabi-as',str(t/'input.s'),'-o',str(t/'input.o')],check=True);rawtext=subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-j','.text','-M','force-thumb','--adjust-vma='+hex(start),str(t/'input.o')],text=True)
rows=[];cursor=start
for line in rawtext.splitlines():
 m=re.match(r'\s*([0-9a-f]+):\s+([0-9a-f]{4}(?: [0-9a-f]{4})?)\s+([^\s]+)\s*(.*)',line)
 if not m:continue
 a=int(m[1],16)
 if not start<=a<end:continue
 raw=b''.join(int(v,16).to_bytes(2,'little') for v in m[2].split());assert a==cursor and raw==d[a-0x438000:a-0x438000+len(raw)];cursor+=len(raw);rows.append(dict(address=a,bytes=raw.hex(),mnemonic=m[3],operands=m[4]))
assert cursor==end,(hex(cursor),hex(end),rawtext)
o=b/'analysis/review-isolated-P2-21349/fresh';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Floating scale rational correction and exponent width selection\n\nPartial/unaccepted;136 instruction bytes 483798..483820. Continuation of 48364C64-byte frame. Ordered binary64 operations: d4=d4+d6(10); d4=d1/d4;d6=6;d4=d4+d6;d1=d1/d4;d1=d3+d1;d1=d2/d1;d3=1;d1=d1+d3;d2=fullSP0;d1=d1*d2;store d1SP0;reload d1SP0;compare original magnitude d0,d1 and transfer flags. PL skips to4837E8;MI R7--wrapping, reload d1SP0, d3=10, d1=d1/d3, storeSP0.\n\nR2=R7+99mod32; unsigned R2<199 gives R8=4 elseR8=5, preserving wrapped comparison. Test R6bit11 via LSLS20; clear→48383C unresolved. Set loads full8B literal483950→d2 and compares d0,d2; LT→483832 unresolved; otherwise literal483958→d2, compare d0,d2; PL→483832. Otherwise signed compare R7,R0; GE→483824 unresolved; LT R0=R0-R7 wrapping at48381E. Fallthrough483820 unresolved. Literal data remains to recover in full; references only four-byte prefixes. Exact VFP condition codes preserved, including LT versus MI. No C, freeze,wholecoverage or equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
