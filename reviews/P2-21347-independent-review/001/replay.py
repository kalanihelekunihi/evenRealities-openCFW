from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x48370e;end=0x483798
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
o=b/'analysis/review-isolated-P2-21347/fresh';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Floating exponent estimate and scale polynomial middle\n\nPartial/unaccepted;138 instruction bytes 48370E..483798, continuation of 48364C64-byte frame. Operations are ordered scalar binary64 VFP instructions. VMLA d4,d1,d3; d1=full8B SP0; d3=-1.5 immediate; d1=d1+d3; d3=full8B literal483930; VMLA d4,d1,d3. Convert d4 to signed32 s2 by VCVT.S32.F64 (truncate toward zero), rawmove toR7. Rawmove R7tos2; signed32→double d1. Load full8B483938→d3;d4=0.5;VMLA d4,d1,d3; truncate signed32 d4tos2→R2.\n\nR7→s2→signed-double d1;d3=full8B483940;d3=d1*d3. R2→s2→signed-double d1;d4=full8B483948;VMLA d3,d1,d4;d1=d3*d3. R2+=1023 wrapping; R3=ASR(R2,31) then immediately overwritten R3=R2<<20;R2=0;storepairR2/R3 at SP0. The dead arithmetic-shift register write still changes flags before later LSLS/MOVS; preserve instruction effects where needed. d4=2.0;d2=d3*d4;d5=2.0;d3=d5-d3;d5=14.0;d4=d1/d5;d6=10.0. Fallthrough483798 unresolved. Do not replace VMLA with fused VFMA or reorder arithmetic; literal references are four-byte prefixes and full eight-byte data awaits separate recovery. No C,freeze,wholecoverage or equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
