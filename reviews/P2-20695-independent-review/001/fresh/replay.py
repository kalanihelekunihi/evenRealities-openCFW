from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47add4;end=0x47ae26
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
o=Path('reviews/P2-20695-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Record halfword eight byte helper zero counter pointer return\n\nPartial/unaccepted;82 instructionbytes. PUSH R3,R4,R5,R6,R7,LR24-byteframe. R5fullentryR0,R6fullentryR1,R4literal47AE64,R7=10. Loop0x47ADE4testsLOW8 R7zero;zero explicitR0zero at0x47AE22. Otherwisefreshbyte[R4+47]zero skips;freshunsignedhalfword[R4+76]compareLOW16 R5,unequalskips. Passingrecordcalls0x4751C8(R4+68modulo2^32,fullR6,8,liveR3);fullresultnonzero skips. Skiptail0x47ADE0decrementsR7andadvancesR4by200modulo2^32;tenrecords. No byte48guard;helperresultzero selectsrecord,oppositeprevioushelperguard.\nSelectedrecordloadsR0literal47AE50,freshword[R0]R1,incrementmodulo2^32andstoreback;independentlyreloadword[R0]R0andstorefullword[R4+196]. SetR0fullR4,branchshared0x47AE24. POP R1,R4,R5,R6,R7,PCrestores24frame;R1savedentryR3,R0selectedpointerorzero. Preservefreshcounterread/reload,livehelperargs,nounprovedhelpercontract. No C,freezeorcompletenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
