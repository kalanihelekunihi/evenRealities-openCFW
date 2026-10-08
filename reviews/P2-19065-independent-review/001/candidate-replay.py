from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x468e8e;end=0x468f04
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selectors74-8-64-default-diagnostics-and-shared-return1-19466-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Dispatchtail468E8E..468F04\n\nPartial,unaccepted;118instructionbytes.Inherited24frame,R4FULLoriginalR2selector,R5originalR3. FULLR4==74:45A568(originalargs)FULLresult==2andnot2branches BOTHsetR0=1->468F02;no actioncall,retainpredicateeffect. ElseFULLR4==8:45A568(originalargs)FULLresult==2skipactionR0=1->468F02;otherR1R5,R0R4,liveR2/R3 to4A8E6C;R0=1->468F02. ElseFULLR4==64diagnostics,other->468F00R0=1.\n\nCase64fresh43D0CEbit1setSP4literal469138,SP0=562,R3literal469110,R2literal4690DC,R1literal4690E0,R0=4 to43D574. Separatefreshbit0 orconditional thirdbit2 R1literal46913C,R2R1,R0=0x10000000,liveR3 to43CE9E. R0=1->468F02.\n\nShared468F02POP R1/R2/R3/R4/R5/PC consumes24frame. R0=1onallrecordedreturnarms. R1fromSP0originalR1orlastdiagnosticline,R2fromSP4originalR2orcontext,R3fromSP8originalR3orcase66word;R4/R5restored. No predicate/childcontracts inferred;followingliteralpool excluded. Exactreplay only,no gates/runtime/acceptance.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
