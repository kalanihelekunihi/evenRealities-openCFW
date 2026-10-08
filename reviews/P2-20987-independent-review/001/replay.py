from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47e712;end=0x47e75a
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-caller-object-wrapper-fatal-checks-stack-forwarding-21386-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text("# Caller-supplied forty-four-byte object wrapper with retained fatal checks\n\nPartial/unaccepted;72instructionbytes47E712..47E75A. PUSH R1,R2,R3,R4,R5,LR24. SP0=44 overwritessavedentryR1;freshreloadSP0→R4;fullR4!=44→5FA0A4(liveargs),ifreturnsstoreword0toFFFFFFFFthenselfloopE72Aifstorecompletes. Thisstored/reloadedcheckretained,notdiscardedbecauseordinarylocalexecutionmakesitequal.\nR4=freshSP28 (caller'ssixthstackarg);R5=freshSP0. R4zero→secondfatalcall/write/selfloopE740. AtE742againfullR4zero skipswork(return0);withoutregistermutationinbetweenthatbranchisunreachablefromnormalnonzeropathbutinstructionretained.\nNonzero→byte[R4+40]=2;SP4=R4 overwritessavedentryR2;R5=freshSP24(caller'sfifthstackarg);SP0=R5;47E75A(liveentryR0,R1,R2,R3)withstackargsfifthcallerword,sixthR4. R0=R4;POP R1,R2,R3,R4,R5,PC24 returnsR1=SP0,R2=SP4,R3=SP8savedentryR3,subjectcallee memorywrites;restoresentryR4/R5. Helperresultdiscarded. Exactobjectownership/helpersemanticsunresolved; no C/freeze/completenessclaim.\n")
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
