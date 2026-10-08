from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x481e80;end=0x481ee6
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
o=b/'analysis/review-isolated-P2-21221/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Hex float helper chain and seven-nibble backward buffer loop\n\nPartial/unaccepted;102 instruction bytes481E80..481EE6. Continues481836232frame,R4/R5workingpair,R6buffercursor,R7budget. Loopcall43C0B0(R0R4,R1R5,R2=0,R3=0);returnedcarryset→481EE6 unresolvedrounding. Carryclear:R2=28,call4D41F4 withliveR0/R1/R3;returnpair→R4/R5. Call4D42F8 withreturnpair/liveotherargs;R8fullreturnR0;R7-=7mod2^32. IfsignedR7>0 call4D4306 withliveargs;returnpair→R2/R3;R0/R1workingR4/R5;call4D4314;returnpair→R4/R5. Helpersemanticsremainexplicitdependencies.\n\nR0=R6+7mod2^32,R1=7. IfsignedR8>0:R1--updatesflags;ITTT PL conditionalR2=R8&15,predecrementR0storebyteR2,R8=ASR(R8,4). BPLusesflagsfromR1decrement,loopsbacktofreshCMP R8. IfR8<=0orR1becomesnegative,join481EDC. Zero-fillloopdecrementsR1thenifPL R2=0,predecrementR0storebyte0,repeat. Preserveseparateddecrementtests:atmostsevennibble/zerobytes;rawdigits0..15 notASCIIyet. R6=R0+7;ifsignedR7>0repeathelperloopelsefallthrough481EE6. No replacementwithordinaryhexformatting/C/freeze/fullcoverage/equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
