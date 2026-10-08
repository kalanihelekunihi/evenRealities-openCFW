from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47e8f2;end=0x47e93c
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
o=b/'analysis/review-isolated-P2-20997/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text("# Nested state boolean output and unsigned counter observation\n\nPartial/unaccepted;74instructionbytes47E8F2..47E93C,twoentries.\nE8F2frameless:R2=literalEB78pointer;freshword[R2]→R1;freshword[R1]intoR1. Fullzero→R1=1,nonzero→R1=0;writeword[entryR0]=R1. Independentlyfreshreloadword[entryR0]intoR0. Nonzero→R0=0return. Zero→independentlyfreshword[R2],freshword[result+12],freshword[result]→R0return. R1retainspreviouslycomputedboolean,R2retainspointer,R3unchanged. Outputpointermayaliaschainmemory,sofreshreloadandsecondchainmustremainafterwrite;don'tsimplifytonulltestcachedsnapshot. No nullchainguards.\nE916 PUSH R4,R5,R6,LR16;R4=entryR0outputpointer;454EFE(liveargs)→R5fullcounter;R6=literalEB80pointer;freshpreviousword. UnsignedR5<previous→47EA90(liveargs),thenword[output]=1;otherwiseword[output]=0. BothpathsstoreR5word[R6]afteroutputwrite;R0=R5returns. Output/globalpointeralias/orderretained,helperreturnignored. POP R4,R5,R6,PC restorespreservedregs. Refines21394output-helperdependenciesbut47EA90/454EFEsemanticsremainunresolved. No C/freeze/completenessclaim.\n")
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
