from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x460302;end=0x460344
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-byte-ring-removal-loop-and-selected-length-return-18876-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Removal loop460302..460344\nPartial;unaccepted.66 instructionbytes,inheritsframe12/R0outputpointer/R1selectedlength/R2counterzero/R3ringbasefrom4602CA. Initialentryfromprefixbranches460330testbeforebody.\n460302:R4=freshhalf[R3+258];R4=freshbyte[wrap32(R3+R4)];R5=low16R2;byte[wrap32(retainedoutputR0+R5)]=low8R4. SEPARATEfreshhalf[R3+258]→R4 AFTERoutputstore;R4+=1,R5=256,R6=SDIVsigned(R4,R5),R4=wrap32(R4-R5*R6)viaMLS;half[R3+258]=low16R4. Freshhalf[R3+260]→R4 AFTERindexstore;R4-=1;half[R3+260]=low16R4. R2=wrap32(R2+1).\n460330:R4=low16R2,R5=low16R1;unsignedR4<R5→460302;otherwiseR1=low16R1,R0=R1. 460340POP{R4,R5,R6},460342BXLR restoreoriginalsavedregs,returnselectedlow16length. Prefixfailurejoins460340preserveFFFFFFFD(nulloutput/low16lengthzero)or0(initialemptycount). No outputnullguard inloop;aliasescanmodifyfreshreadindex/count,recordbyteaddressusesunmaskedhalfindexbeforemodulo update. No countrecheckperiteration;selectedlengthfixedinR1. No childcallsorlock. Next460344excluded.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
