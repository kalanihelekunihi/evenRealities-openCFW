from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4696fa;end=0x46976a
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selector2-resource-result-forwarding-and-offset16-20-child-stores-19516-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Resource forwarding and child stores 0x4696FA..0x46976A\n\nPartial/unaccepted;112instructionbytes. Inherit32frame,R4globaladdressliteral469B98. R5=literal469BA4, overwritingoriginalR3snapshot. R0=R5 ->460084(liveotherargs);R1=FULLresult,R0=R5 ->45FFFE(liveR2/3);R1=FULLresult,R0=freshword[R4+4] ->49942E(liveR2/3). Then43F6B8(freshword[R4+4],2,0,32).\n\nFreshword[R4] ->498668(liveotherargs);storeFULLresult[R4+16]. Call43F09A(freshword[R4+16],212,148,live3),498680(freshword[R4+16],literal469BA8,live2,live3),43DFA4(freshword[R4+16],16,live2,live3).\n\nIndependentlyfreshword[R4] ->498668(liveotherargs);storeFULLresult[R4+20]. Call43F09A(freshword[R4+20],323,148,live3),498680(freshword[R4+20],literal469BAC,live2,live3),43DFA4(freshword[R4+20],16,live2,live3). Eachwordreloaddistinctafterchildsideeffects. R4globaladdress andR5literalremainliveat46976A. No resource/text/geometrycontracts inferred; no C,freezeorwholefunctionclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
