from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x522ae0;end=0x522b30
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
o=Path('/tmp/review2-graphics-packed-rectangle-command-16366');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Packed rectangle-command candidate, 0x522AE0..0x522B30\n\n80 original bytes; partial/accepted:false. PushR4..R7/LR20 +local4, total24.\nR6=entryR2; R4=entryR0; R5=entryR1; R7=entryR3\nCMP signed R6,1; if GE: CMP signed R7,1\nif resulting APSR.N!=APSR.V: goto522B2C\nR0=3; call514AEC()\nif R0==0: goto522B2C\nR2=(R4&FFFF)|((R5<<16)&FFFF0000)\nR1=260; word[R0]=R1; word[R0+4]=R2\nR5=u32(R7+R5); R4=u32(R6+R4)\nR2=(R4&FFFF)|((R5<<16)&FFFF0000)\nR1=264; word[R0+8]=R1; word[R0+12]=R2\nR1=word[0x5232CC]; word[R0+16]=R1\nR2=word[0x5232D0]; R3=word[R2]; R1=word[R3+24]; R1=R1|2; word[R0+20]=R1\n522B2C: SP+=4; restoreR4..R7/PC fromsavedframe; SP+=20; return\n\nWidths/heights rejected if signedless1; compare uses conditionalIT execution, not unsigned. RejectedentryR0 retained, childNULL returns0, successR0 allocatedpointer. Literal5232CC FF000100,5232D0 20074EFC outsidecode. Allocator/output ownership/capacity/ABI and globalpointer lifetime unresolved; stores precede global reads, preserve alias/fault ordering. No exactrectangle physical qualification or C/admission/gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
