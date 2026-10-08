from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x482b00;end=0x482b56
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
o=b/'analysis/review-isolated-P2-21281/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Aligned size and two-pointer initialization, node prepend\n\nPartial/unaccepted;86 instructionbytes482B00..482B56. Frameless482B00: R2=0 store[R0+4],R2=0 store[R0+8];R1+=3mod2^32,logicalright2thenleft2,store[R0];BXLR. Thus alignedsize=(entryR1+3mod)&FFFFFFFC; no overflowguard; ordered fieldwrites before size.\n\nSeparate482B12 PUSH{R3,R4,R5,LR}16bytes;R5=entryR0descriptor;freshword[R5]→R0,add8mod;call44F718 liveR1/R2/R3;returnedR0→R4. ZeroR4 skipsalllinkwrites returns0. Nonzero: R2=0,R1=R4,R0=R5,call482DAE liveR3. Freshword[R5+4]→R2,R1=currentR4,R0=currentR5,call482DC2 liveR3. Freshword[R5+4]→R0,ifnonzero independentlyreload[R5+4]→R1,R2=R4,R0=R5,call482DAE liveR3. StoreR4[R5+4] thenfreshword[R5+8]zero→storeR4[R5+8];nonzero retains. R0=R4,POP{R1,R4,R5,PC}16bytes;R1=savedentryR3. Linkhelper semantics unresolved; no allocationownershipassumption or C. No freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
