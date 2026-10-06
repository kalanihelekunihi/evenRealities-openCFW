from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x460898;end=0x460910
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
o=Path('/tmp/p2-18507-fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Header dispatch/mismatch460898..460910\nPartial;unaccepted.120 instructionbytes,inherits64frame/locals36,R5headerbyte0,R4headerbyte1,R6headerhalf2,R7buffer. 460898R0=0x10C00000;43CE9E withR1/R2literal461360,R3low8headerR5 andlocalSP0/4argsfrompriorcandidate. 4608A0R0=low8R5;nonnull→460D06externalbranch. ZeroR0=low16R6;fullR0!=3→460CA8externalbranch. Exact3R5=wrap32(R7+4),REPLACESheaderbyte;R0=freshhalf[R5+4] FIRST,R1=freshword[R5] SECOND;fullR0==R1→460920externalmatch. Unequal→43D0CE liveR0/R1/R2/R3;bit1clear→4608EC. SetorderedR0=FRESHword[R5]→SP12,R0=FRESHhalf[R5+4]→SP8,SP4=wordliteral461364,SP0=422,R3=wordliteral4611B8,R2=wordliteral4611BC,R1=wordliteral4611C0,R0=1;43D574. DiagnosticreadorderWORDthenHALF differsfrominitialcomparisonHALFthenWORD.\n4608ECfresh43D0CE bit0set→4608FC;otherwiseSEPARATE43D0CE bit2clear→460910externaljoin,set4608FC. 4608FC:R1=wordliteral461368 FIRST,R0=FRESHword[R5]→SP0,R3=FRESHhalf[R5+4],R2=R1,R0=0x04800000;43CE9E. Freshfieldreadsinbothdiagnosticsnotreusecomparisonvalues;no latercompareinspan. Localwritesnot savedslots. Next460910/epilogueoutside span. Childcontracts unresolved.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
