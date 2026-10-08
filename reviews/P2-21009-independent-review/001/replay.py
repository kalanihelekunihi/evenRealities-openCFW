from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47eb94;end=0x47ebf8
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-thirty-two-byte-caller-allocation-object-init-21408-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Thirty-two-byte caller object and allocation initialization\n\nPartial/unaccepted;100instructionbytes47EB94..47EBF8,twoentries.\nEB94 PUSH R2,R3,R4,LR16;R4=entryR0. Fullzero→5FA0A4(liveargs),ifreturnsstore0toFFFFFFFFthenEBA8selfloop. OtherwiseSP0=32overwritessavedentryR2;freshSP0reloadfull!=32→samefatalwrite/selfloopEBC0. Retainstored/reloadedguarddespiteordinaryequality. FullR4zeroagainatEBC2skipinit;normalpathnonzero→word[object]=0;45607C(object+4,liveargs);byteobject28=1. ReturnR0=R4;POP R1,R2,R4,PC returnsR1=SP0(32onordinarypath),R2=savedentryR3subjectcallee writes,restoresR4.\nEBD8 PUSH R4,LR8;456110(32,liveentryR1,R2,R3)→R4. Fullzero→return0. Nonzero→word[object]=0;45607C(object+4,liveargs);byteobject28=0. ReturnR0=R4,discardinitializationhelperresult;POP R4,PC restoresR4. Callerobjectbyte28=1versusallocationbyte28=0 keptdistinct;otherfieldinitializationdepends45607C. No C/freeze/completenessclaim;ownership/externalhelpersemanticsunresolved.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
