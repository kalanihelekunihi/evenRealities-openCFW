from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4604c2;end=0x460524
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
o=Path('/tmp/p2-18487-fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Buffer transform prefix4604C2..460524\nPartial;unaccepted.98 instructionbytes,opencontinuation. STMDBSP!{R3,R4,R5,R6,R7,R8,R9,LR}frame32 THEN SUBSP48:total80,localsSP0..47,savedR3/4/5/6/7/8/9/LR at48/52/56/60/64/68/72/76. R4=incomingR0,R5=incomingR1. R1=892,R2=0,R6=wordliteral460E14,R7=R6,R0=R7;43C0E4 liveincomingR3. R7=1074 REPLACESfirstbufferalias;R1=R7,R2=0,R8=wordliteral460E18,R9=R8,R0=R9;43C0E4 livepreviouschildR3.\nOrderedR0=1,byte[R6]=1;byte[R6+1]=low8retainedR4;R0=4,half[R6+2]=4;R5=low8R5 REPLACESfullinput;word[R6+4]=zeroextendedR5. R2=retainedR7(1074),R1=retainedR8,R0=SP+28;4905F4 liveR3. R0=SP+8,R1=SP+28,R2=20;439C04 liveR3. R2=retainedR6,R1=wordliteral460E1C,R0=SP+8;490C32 liveR3. Fullnonnullresult→460568externalcontinuation;zero→460524diagnosticexcluded. Childcontracts unresolved;do not assume clear/copy/serializationcontracts or initializedstackcontents. Passedstackpointersallowchildwrites,includingaliasoverlaps. No inputnullguards;buffersareliteralvaluesnotdereferencedglobals. Epilogue/remainingbranchesoutside span.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
