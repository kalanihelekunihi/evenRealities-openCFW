from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x46966a;end=0x4696fa
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selector2-second-object-and-offset4-ordered-child-configuration-19514-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Ordered second object calls 0x46966A..0x4696FA\n\nPartial/unaccepted;144instructionbytes. InheritedR4globaladdressliteral469B98. Orderedcalls43F4C0(freshword[R4],576,288,live3),43F09A(freshword[R4],0,0,live3),43DFA4(freshword[R4],16,live2,live3),44129E(freshword[R4],0,0,live3),44131C(freshword[R4],0,0,live3),46916C(freshword[R4],0,0,live3). Freshword[R4] ->499416(liveotherargs); storeFULLresult[R4+4].\n\nCall43F4C0(freshword[R4+4],484,90,live3);44145A(freshword[R4+4],2,0,live3). R0=bitwiseNOT0xFF000000=0x00FFFFFF ->44104C(liveotherargs);R1=FULLresult,R2=0,R0=freshword[R4+4] ->44140E. R2=0,R0=literal469BA0,R1=freshword[R0],R0=freshword[R4+4] ->44143E withliveR3. Orderedfreshpointercalls44129E(...,0,0,live3) then44131C(...,0,0,live3), eachR0freshword[R4+4]. No cachedpointerreplacement; fullresultwords andsourcewordreadretained. R4globaladdressliveat4696FA. No geometry/color/creationcontract inferred; no C/freeze/runtimeclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
