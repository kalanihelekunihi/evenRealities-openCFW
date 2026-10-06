from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4603de;end=0x460424
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
o=Path('/tmp/p2-18481-fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# State routine continuation4603DE..460424\nPartial;unaccepted.70 instructionbytes,inheritsframe16savedR5/R6/R7/LR slots0/4/8/12 andnonnulllookupR0from460374. R1=250;word[lookupR0+12]=250. 43D0CE liveR0lookup/R1=250/R2/R3;bit1clearviaLSLS30/BPL→460404. Bit1setorderedR0=wordliteral460E10→SP4,R0=287→SP0,R3=wordliteral460D64,R2=wordliteral460628,R1=wordliteral46062C,R0=4;43D574 liveargs. SP8notwrittenbyseconddiagnostic;retainprefix250ororiginalR7.\n460404 fresh43D0CE bit0set→460414;otherwiseSEPARATE43D0CE bit2clear→460422,bit2set460414. 460414:R1=wordliteral461028,R2=R1,R0=0x10000000;43CE9E liveR3. 460422POP{R0,R1,R2,PC}:SP0/4/8→R0/R1/R2,LR→PC;R5/R6/R7nevermodified. Childresultsdiscarded;R0savedincomingR5or279fromprefixdiagnosticor287fromseconddiagnostic. R1savedincomingR6orprefixliteralD60orsecondliteralE10;R2savedincomingR7orprefix250. Second diagnosticoverwrites onlySP0/4. Prefixnullglobal/nulllookupjoin skipsrecordstoreandallsecondmaskcalls. Allmaskcallsfresh;no additionallookups/bytewritesinspan. Next460424excluded.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
