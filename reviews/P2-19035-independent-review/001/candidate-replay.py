from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x468920;end=0x4689de
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-payload-cases15-16-diagnostics-halfword-stack-builders-19436-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Payloadcases15/16 468920..4689DE\n\nPartial,unaccepted;190instructionbytes.Inherited40frame,R4FULLthirdarg,R5payload,R6FULLpredicate,R7byte15or16. No additionalpayloadlengthcheckinthisinterval;entrynonnullR4previouslyrequired.\n\nCase15fresh43D0CEbit1setSP4literal4690B4,SP0=361,R3literal468F08,R2literal468A38,R1literal468A3C,R0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 R1literal4690B8,R2R1,R0=0x0C000000,liveR3 to43CE9E. TruncateR6inplace low8;!=1->46897C. Equal1:R0literal4690BC,THENfreshhalfword[R0]toR0;storehalfwordSP4 overwritinglow16previousSP4diagnosticcontext;R3=0,R2=2,R1SP4,R0=16 to464BB2. Branch46897C->468A28.\n\nCase16freshbit1setSP4literal4690C0,SP0=374,samecommonargsR0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 R1literal4690C4,R2R1,R0=0x0C000000,liveR3 to43CE9E. TruncateR6inplace low8;!=1->4689DC. Equal1:R0literal4690C8,THENfreshhalfword[R0]toR0;storehalfwordSP2 overwritingupper16previousSP0diagnosticline;R3=0,R2=2,R1SP2,R0=16 to464BB2. Branch4689DC->468A28. Childcontracts/halfwordmeaningunproven;exactreplay only,no gates/runtime/acceptance.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
