from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x48426c;end=0x4842d0
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
o=b/'analysis/review-isolated-P2-21407/fresh';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Size adjustment tail and resource release counter prefix\n\nPartial/unaccepted;100 instructionbytes48426C..4842D0. Continuation48423424Bframe: storeR8(current-oldsize)word[objectR5+8];R0=R4newresource,4D05E4;freshcurrentR1,R0+=R1wrap,storecurrent. FreshhighwaterR0/currentR1,unsignedhigh>=current→freshhighwaterelsefreshcurrent;storehighwater. R3/R2/R1=0,R0=freshobjectword0;4417EE;R0=R4result;POP R4/R5/R6/R7/R8/PC24B. Earlierguardfailure jumpsresultreturnwithoutrelease,operationnull skipscounterupdatesbutreleases.\n\nNew48429EPUSH R4/R5/R6/LR16B;R5=entry0object,R4=entry1resource;resourcezero→4842E4unresolved. NonzeroR1=FFFFFFFF,R0=word[object];441C44;result!=1→4842E4. EqualR0=R4,4D05E4→R6size;R1=R4,R0=word[object+4];4D0808ignoredresult;freshcurrentR0, unsignedR6>=R0→4842D4unresolved;elsefreshcurrentR0again,R6=R0-R6wrap. Fallthrough4842D0unresolved. Retaincurrentmutationafterhelperandfreshreads,nohelpercontractassumption. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
