from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4833a6;end=0x483424
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
o=b/'analysis/review-isolated-P2-21331/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Floating special sign, range fallback and magnitude\n\nPartial/unaccepted;126 instructionbytes4833A6..483424,continues48335080-byteframe. VLDRd2from483620eightbytes,VCMPd0,d2/VMRSflags;NE→4833DE. EQflagsR12bit2set→R4=4,R5=freshwordliteral483FFCpointer;clear→R4=3,R5=ADR483628. OrderedstoresR12SP12,R6SP8,R4SP4,R5SP0;call48306C liveentryR0/R1/R2/R3,branch48360Cunresolved.\n\n4833DEfreshSP80fifthargument→R7;VLDRd2from48362Ceightbytes;VCMPd0,d2/VMRS;GE(N==V)→4833FC. OtherwiseVLDRd2from483634eightbytes,VCMP/VMRS;PL(N==0)→48340A,MI→4833FC. FallbackorderedstoresR12SP8,R6SP4,R7SP0;callunresolved48364C withliveentryR0/R1/R2/R3andd0,branch48360C. At48340A LR=0;VLDRd2from48363Ceightbytes,VCMPd0,d2/VMRS;PLskipto483424;MI LR=1,VNEG.f64d0,d0. Fallthrough483424. PreserveexactFPconditions(varyGE/PL),flagreadbit2,8byteconstantobligations(genericreferencesonly4byteprefixes),livehelperargsandorderedstores. No assumedinfinity/rangevaluesbeforedatareview. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
