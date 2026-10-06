from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x460374;end=0x4603de
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-diagnostic-two-hundred-fifty-state-word-and-key-three-lookup-prefix-18880-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Diagnostic/state lookup prefix460374..4603DE\nPartial;unaccepted.106 instructionbytes,opencontinuation. PUSH{R5,R6,R7,LR},frame16 slots0/4/8/12. 43D0CE liveincomingargs;bit1clearviaLSLS30/BPL→4603A0. Bit1setorderedR0=250→SP8,R0=wordliteral460D60→SP4,R0=279→SP0,R3=wordliteral460D64,R2=wordliteral460628,R1=wordliteral46062C,R0=3;43D574 liveargs. SP0/4/8alias savedR5/R6/R7. 4603A0 fresh43D0CE bit0set→4603B0;otherwiseSEPARATE43D0CE bit2clear→4603C0,bit2set4603B0. 4603B0:R1=wordliteral460D68,R3=250,R2=R1,R0=0x0C400000;43CE9E liveargs.\n4603C0:R0=250,R1=wordliteral460E08;word[R1+12]=250. R2=wordliteral460E0C globaladdress,R0=freshword[R2];fullzero→460422externalepilogue. NonzeroR1=3,R0=SEPARATEfreshword[retainedR2globaladdress],no secondnullretest;45F840 liveR2/R3;fullzeroresult→460422,nonnullfalls4603DE nextinstructionexcluded. Freshmaskreads andglobalreloadnotmerged;postdiagnosticglobalwordstoreunconditional. Childcontracts unresolved;epilogue/remainingwritesoutside span.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
