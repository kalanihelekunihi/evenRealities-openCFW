from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47dd62;end=0x47ddac
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
o=b/'analysis/review-isolated-P2-20931/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Conditional helper dispatch and saved-stack-word returns\n\nPartial/unaccepted;74instructionbytes47DD62..47DDAC,threeentries.\nDD62 PUSH R7,LR8;443484(liveentryargs). Fullresultnonzero: R0=0 thenSP0=0 overwrites savedR7;R3=0,R2=2000,R1=4;R0=freshword[pointerliteral47E28C];47E7B0(R0,4,2000,0) withstackwordSP0=0. ThenPOP R0,PC returnsSP0 (zero absent callee mutation),not calleeR0. Fullfirstresultzero:448F98(liveargs),thenPOP R0,PC returns savedentryR7 subjectto helperstackeffects. No boolean normalization of firsthelper result.\nDD8A PUSH R7,LR8;callDD62(liveargs);POP R0,PC returns this outer savedentryR7,discarding innerreturn. Stackframes remain distinct; innerSP0zero doesnot overwriteouterSP0 under ordinary local writes.\nDD92 PUSH R7,LR8;R0=freshword[pointerliteral47E28C]. Ifzero skip allwrites/helpercalls. OtherwiseR0=0,R1=literal47E290 pointer;storeword0there thencallDD62withliveargs. POP R0,PC returns own savedentryR7,discarding helperreturn. Preserve write-before-call and no entryR0parameter retention. Externalhelpereffectsand literalownership unresolved;no C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
