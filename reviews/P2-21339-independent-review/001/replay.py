from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x48355c;end=0x48360c
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
o=b/'analysis/review-isolated-P2-21339/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Floating integer digits, zero width, sign and output\n\nPartial/unaccepted;176 instructionbytes48355C..48360C,continues48335080-byteframe. WhileunsignedR8<32: R4=10,R7=SDIV(R5,10)towardzero,R4=R5-10*R7mod,add48;R7=SP16buffer,storelowbyteR4[buffer+R8],R8++;R4=10,R5=SDIV(R5,10);nonzeroR5repeat,zerobreak. Atleastonedigitifspace;actualsignedremainder preserved.\n\nFlagsR12&3==1 enableszero-widthpadding. IfR6width!=0 and(UXTB(LRsign)!=0 OR(flags&12)!=0),R6--mod. LoopunsignedR8<R6andR8<32 writesASCII48SP16+R8,R8++;otherwiseends. Flagsotherpatternskippadding. Ifcount<32: LR=UXTB(LR),nonzeroappend45minus;zero flagsbit2append43plus;elseflagsbit3append32space;else none. Allsignstoresbeforecountincrements;priorityminus/plus/space.\n\nOrderedstackargsR12flagsSP12,R6adjustedwidthSP8,R8countSP4,R4=SP16buffer→SP0;call48306C withretainedentryR0/R1/R2/R3 (nocallswithinnormalpathsincelastentrychecks). Fallthrough48360Creturnunresolved. Preservefullcountbound,unsignedpaddingversussigneddigitdivision,byteLRsignandwrappingwidthadjustment. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
