from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x540372;end=0x5403c8
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
o=Path('reviews/P2-15933-failed-function-second-region-transform-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Second region transform continuation, 0x540372..0x5403C8\n\nPartial; accepted:false. 86 original bytes; active224-byte frame.\n\nR0=SP+112; R1=word[0x5409D8]; word[R0+16]=R1\nR1=word[SP+12]; R1=u32(R1-R6); S0.bits=R1; S0=VCVT.F32.S32(S0); word[R0+8]=S0.bits\nR1=word[SP+16]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R7)\nS0.bits=R1; S0=VCVT.F32.S32(S0); word[R0+20]=S0.bits\nR0=SP+112; call561B38()\nR0=SP+112; call5226E8()\nR3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)\nR2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)\nR1=word[SP+32]; R1=u32(R1-R7)\nR0=word[SP+28]; R0=u32(R0-R6)\ncall522AE0(); continue5403C8\n\n5409D8 is literal data outside this code span, explicitly recorded by PC-relative reference. Conversion uses signed interpretation of wrapped32 and architectural binary32 conversion with floating-point rounding controls, with floating status/trap/enable conditions unresolved. Child return values overwritten; child contracts and effects unresolved. Join5403C8 also reached from preceding skip branches. No C, admission, gate or physical rendering qualification.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
