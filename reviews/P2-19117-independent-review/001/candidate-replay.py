from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x46976a;end=0x4697ec
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selector2-offset8-12-stores-branch-tail-and-alternate-entry-19518-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Branch tail and alternate entry 0x46976A..0x4697EC\n\nPartial/unaccepted;130instructionbytes. InheritedR4globaladdress. Freshword[R4] ->498668(liveargs),FULLresultstore[R4+8]. Ordered43F09A(freshword[R4+8],373,198,live3),498680(freshword[R4+8],literal469BB0,live2,live3),43DFA4(freshword[R4+8],16,live2,live3). Independentfreshword[R4] ->498668(liveargs),FULLresultstore[R4+12]. Ordered43F09A(freshword[R4+12],180,198,live3),498680(freshword[R4+12],literal469BB4,live2,live3),43DFA4(freshword[R4+12],16,live2,live3). R0=0;storeword0[R4+24];branch4698DC outsidechunk.\n\n4697BAalternateentryfrombytezero guard4695FA, withR5originalR3 preserved (doesnotpassresourceR5replacementat4696FA). R6=literal469B9C,R0=R5 ->43DE82(liveargs),FULLresultstore[R6]. Ordered43F4C0(freshword[R6],576,288,live3),43F09A(freshword[R6],0,0,live3),43DFA4(freshword[R6],16,live2,live3). R0=0 ->44104C(liveargs),FULLresultliveat4697EC. Preserveorderedfreshreloads anddistinctbranchregisterstate. No C,freezeorchildcontractclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
