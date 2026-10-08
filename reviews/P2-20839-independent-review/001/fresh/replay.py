from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47cc60;end=0x47ccd2
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
o=b/'analysis/review-isolated-P2-20839/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Two-word division small divisor fast paths\n\nPartial/unaccepted;114 instruction bytes. EntryR1:R0 numerator,R3:R2 divisor. CC60 ifR3nonzero→pendingCCD2;otherwiseifR1zero→CC9E. NonzeroR1:unsignedR2>=65536→pendingCD68;elseCMP R2,2 and<=2→CCAE.\nFor3..65535:IP=oldR1;R1=UDIV(oldR1,R2);R3=oldR1-R2*R1;R3=(R3<<16)|(oldR0>>16);IP=UDIV(R3,R2);R3-=R2*IP;R0=LOW16(oldR0);R3=R0|(R3<<16);R0=UDIV(R3,R2);R2=R3-divisor*R0;R0|=IP<<16;R3=0;BXLR. Thus quotientR1:R0 and remainderR3:R2; preserveintermediateIP.\nCC9E (entryR1zero):CMP R2,2;<=2→CCAE;elseIP=oldR0,R0=UDIV(oldR0,R2),R2=oldR0-divisor*R0;BXLR;R1/R3 remainzero.\nCCAE CBZ R2→CCC4 withoutalteringCMPflags;BNE CCBE uses precedingCMP R2,2. ThereforeR2==2:remainderR2=oldR0&1;LSRS R1,1 setscarryoldR1bit0;RRX R0 usingcarry;BXLR. R2==1:CCBE setsR2=0,R3=0;quotientunchanged;BXLR. R2==0:CCC4 tailbranch4D2B98 withlivearguments; nozero-divisorresultassumed.\nSeparateentryCCC8 copiesR1toR3,R0toR2,zerosR1/R0,BXLR. No fallthroughfromunconditionalCCC4branch; callers/ownershipofCCC8unproven. No frame inthismap. Pendinglargedivisorpaths remain. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
