from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x540078;end=0x5400b8
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
o=Path('reviews/P2-15915-failed-function-expanded-bounds-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Expanded bounds continuation, 0x540078..0x5400B8\n\nPartial; accepted:false.64 bytes of candidate540036..5409C4, not standalone. Entry frame224 active; R5/R8 from previous prefix. Repeated ordered computations:\n\nR2=word[SP+148];R1=SDIV(s32(word[R5+36]),2);R3=2;R2=u32(R2-R1-1);word[SP+44]=R2\nR2=word[SP+156];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R1+R2+1);word[SP+52]=R2\nR2=word[SP+152];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R2-R1-1);word[SP+48]=R2\nR2=word[SP+160];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R1+R2+1);word[SP+56]=R2\ncontinue5400B8\n\nSigned division truncates towardzero, unlike arithmetic shift for negative oddvalues; denominator2 nonzero. All subsequent additions/subtractions wrap32. R0 unchanged; R1/R2/R3 finalscratch as above, no child/extraSPchange. Repeatedpointee loads not collapsed. Fullfunction bounds/ABI/fault/alias/concurrency unresolved; no C/admission/gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
