from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4607b0;end=0x46082e
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
o=Path('/tmp/p2-18503-fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Transform result and error diagnostics4607B0..46082E\nPartial;unaccepted.126 instructionbytes,inherits64frame/locals36,R7bufferbasefrommode0. R0=SP+20,R1=SP,R2=16;439C04 liveR3. R2=retainedR7,R1=wordliteral460E1C,R0=SP+20;490120 liveR3. R0=low8fullchildresult;nonnull→460834externalsuccess. Zero→43D0CE liveargs;bit1clear→460802. Set:R0=freshword[SP32];fullzero→R0=wordliteral461350fallback;nonnullR0=SEPARATEfreshword[SP32]. ThenSP8=selectedR0,SP4=wordliteral461354,SP0=408,R3=wordliteral4611B8,R2=wordliteral4611BC,R1=wordliteral4611C0,R0=1;43D574.\n460802fresh43D0CE bit0set→460812;otherwiseSEPARATE43D0CE bit2clear→46082Eexternalcontinuation,set460812. 460812:R0=freshword[SP32];fullzero→R3=wordliteral461350;nonnullR3=SEPARATEfreshword[SP32],notretainedR0. R1=wordliteral461358,R2=R1,R0=0x04400000;43CE9E. Two diagnosticsmakeindependentSP32reads,notreusefirstselectedpointer. SP32withinlocalframeandmayhavebeenwrittenbytransform;fallbackiswordliteralvalue,notdirectADR. LocalSP0/4/8overwritesearliertransformbytesonlyafterresulttest. Childcontracts unresolved;next46082E/epilogueoutside span.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
