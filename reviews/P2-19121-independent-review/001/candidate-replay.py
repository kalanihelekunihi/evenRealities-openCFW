from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x469878;end=0x4698ee
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selector2-alternate-resource-calls-shared-global-copy-and-zero-exit-19522-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Alternate resource and shared exit 0x469878..0x4698EE\n\nPartial/unaccepted;118instructionbytes. R4globaladdressliteral469B98. Call44145A(freshword[R4+4],2,0,live3);R0=0x00FFFFFF viaMVNFF000000 ->44104C(liveargs),R1=FULLresult,R2=0,R0=freshword[R4+4] ->44140E. R2=0,R0=literal469BA0,R1=freshword[R0],R0=freshword[R4+4] ->44143E(live3). Ordered44129E then44131C each(freshword[R4+4],0,0,live3).\n\nR5=literal469BB8 overwritesoriginalR3snapshot. R0=R5 ->460084(liveargs),R1=FULLresult,R0=R5 ->45FFFE(live2/3),R1=FULLresult,R0=freshword[R4+4] ->49942E(live2/3). Call43F6B8(freshword[R4+4],9,0,0). R0=0;storeword0[R4+24].\n\nShared4698DC (alsoenteredfromnonzero-bytebranch4697B8): R4=literal469B9C;R0=freshword[R4] ->46410A(liveargs); then independentlyfreshword[R4] ->R0,R1=literal469BBC,storeR0word[R1+4]. R0=0;branch469ADE outsidechunk. Retainfreshreadbetweenchildandcopy, branch-specificresourcesandconstants. No C,freezeorchildcontractclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
