from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4684f6;end=0x468558
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-event-zero-child-result-global-state4-and-predicate-branches-19418-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Eventzero4684F6..468558\n\nPartial,unaccepted;98instructionbytes.Inherited40frame,R7event0,R5payload,R4FULLinputthirdarg,R6FULL45A568snapshot. R1=low16R4,R0R5,liveR2/R3 to4A78D0;FULLnonzero->4685E8. Zero:R4literal468C24 replacinginputthirdarg;freshbyte[R4+2]!=2->46862C. Equal2:freshbyte[R4]==4else468546.\n\nStatebyte4:R0=0,liveargs to47E470;THENtruncateR6inplace low8. R6!=1->46862C. Else443484(alllive)FULLresultmust1else46862C;R0=16,liveargs to4434D0 FULLresultmust1else46862C. R3/R2/R1=0,R0=16 to464C36;branch468544->46862C.\n\n468546 non4arm:443484 withR0freshstatebyte,liveR1/R2/R3. FULLzero->468558. NonzeroR0=16,liveargs to4434D0;FULLresult==1->4685B6,othersfallthrough468558. Independentpredicatecalls retained,notmergedwithstate4path. No globalstate/event/childcontracts assumed. Laterdiagnostics/actions excluded;exactreplay only,no gates/runtime/acceptance.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
