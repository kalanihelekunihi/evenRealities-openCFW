from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x46869a;end=0x468722
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-payload-case9-length-three-global-two-byte-update-and-builder-19426-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Payloadcase9 46869A..468722\n\nPartial,unaccepted;136instructionbytes.Inherited40frame,R4FULLinputthirdarg,R5payload,R6FULLpredicate,R7byte9. UnsignedR4<3->468720. Elsefreshbyte[payload+1]overwritesR4,THENfreshbyte[payload+2]overwritesR5(payloadpointerlost). Fresh43D0CEbit1setR0low8R5toSP12,R0low8R4toSP8,SP4literal469098,SP0=297,R3literal468F08,R2literal468A38,R1literal468A3C,R0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 FIRSTR1literal46909C THENR0low8R5toSP0,R3low8R4,R2R1,R0=0x0C800000 to43CE9E;R4/R5byte snapshots preserved.\n\nR0literal468C24;storebyteR4at0 thenbyteR5at1. TruncateR6inplace low8;!=1->468720. Equal1:R0literal4690A0,THENfreshbyte[R0]toR0,storebyteSP0;R3=0,R2=1,R1SP,R0=16 to464BB2. Shared468720->468A28 (distinctfromgeneral468A2A). No length/object/childcontracts inferred beyondobservedunsignedcomparison;epilogueexcluded. Exactreplay only,no gates/runtime/acceptance.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
