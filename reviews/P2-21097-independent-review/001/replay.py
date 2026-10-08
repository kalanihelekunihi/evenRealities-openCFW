from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x480008;end=0x480058
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-single-snapshot-three-byte-output-float-helper-pair-21496-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Single-snapshot three-byte output and float-input helper pair\n\nPartial/unaccepted;80 instruction bytes480008..480058. 0008frameless: R1=0thenliteral4801F4pointer→freshwordR1single snapshot. bits8..9→byte[entryR0+0],bits4..5→byte+1,bits0..1→byte+2,inorder. No nullguard;outputmayaliasinputword,butallfieldsderiveonecachedword. BX LR returnsfullentryR0pointer;R1low2snapshotbits,R2middle2bits.\n\n0028 PUSH R0,R1,R2,R3,R4,LR24;R4entryoutputpointer. VSTR S0raw32bits→SP0 overwrites savedentryR0;480312(2,0,SP,liveR3). Fullhelperzero→freshSP4wordstore[R4],freshSP8wordstore[R4+4],return0;theseareinitiallysavedentryR1/R2andmaybemodifiedbyhelper,donotassumeinitializedlocals. Fullnonzero→word[R4]=0thenword[R4+4]=0,return1normalized. No nullguard;orderedloads/storespreservealiasbehavior. ADDSP16discardsentryslots,POP R4,PC releases8,total24. S0notnumericallyconverted;rawbitsstored. Externalhelpersemantics/ownership unresolved,noMMIO/C/freeze/fullcoverageclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
