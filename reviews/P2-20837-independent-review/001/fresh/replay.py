from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47cc1c;end=0x47cc5e
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
o=b/'analysis/review-isolated-P2-20837/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Two-word sign normalization and flag-dependent helper\n\nPartial/unaccepted;66 instruction bytes. InputpairsR1:R0 andR3:R2. IP=R3&80000000 usingANDS; ifNset negateR3thennegateR2 thenR3=SBC(R3,0) using carryfromlowwordNEG:pairnegationmod64.\nCC2A IP XOR=arithmeticshift(R1,32), flagsupdated;shiftcarry=originalR1bit31. IfZset tailbranch47CC60 withoutframe. This means IPzero; pendinghelperreturnsdirectlytocaller. OtherwisePUSH R4,LR8;R4=IP;BCC CC40 usingcarryfromASR32. Ifcarryone negatepairR1:R0 byNEGhi,NEGlo,SBC hi0.\nCC40 call47CC60 with currentR0..R3,IP. CC44 LSLS R4,1;carry=oldR4bit31,N=newbit31. Ifcarryone negate returnedpairR1:R0;thenTST R4,R4 reestablishN. IfNset atCC52 negate returnedpairR3:R2. POP R4,PC8.\nNo helper arithmetic operation inferred until47CC60 recovered. Preserve flags across branches, lowwordNEGcarryintoSBC,tailbranchvsframedcall. R4encodesentrysigncombination; do not eraseIPsideeffects. No C/freeze/completenessclaim. BytesCC5E..60outsideinstructionmap.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
