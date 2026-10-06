from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x460638;end=0x460694
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
o=Path('/tmp/p2-18497-fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Mode handler prefix460638..460694\nPartial;unaccepted.92 instructionbytes,opencontinuation. STMDBSP!{R4,R5,R6,R7,R8,R9,LR}frame28 THEN SUBSP36:total64;localsSP0..35,savedR4/5/6/7/8/9/LR36/40/44/48/52/56/60. R4=incomingR0,R6=incomingR1,R5=incomingR2. 43D0CE liveincomingargs;bit1clearviaLSLS30/BPL→46066C. Bit1setorderedSP8=retainedR5,R0=wordliteral4611B4→SP4,R0=386→SP0,R3=wordliteral4611B8,R2=wordliteral4611BC,R1=wordliteral4611C0,R0=4;43D574 liveargs. SP0/4/8arelocals,not savedregisterslots.\n46066C fresh43D0CE bit0set→46067C;otherwiseSEPARATE43D0CE bit2clear→46068C,bit2set46067C. 46067C:R1=wordliteral4611C4,R3=retainedR5,R2=R1,R0=0x10400000;43CE9E. 46068C:460178 withliveR0/R1/R2/R3,NOargumentreset. FullR4!=4→460746externalcontinuation;exact4falls460694nextdiagnosticexcluded. Child460178alreadymappedlazyglobalinitializer;returnnotexaminedbeforemodecomparison. R4/R5/R6retainedacrosschildren;no inputguards. Allmaskcallsfreshseparate;remainingmodebranches/epilogueoutside span.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
