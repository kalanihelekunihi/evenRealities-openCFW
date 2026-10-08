from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47ff26;end=0x47ffba
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-mode-two-three-ordered-writes-helper-status-tail-21488-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Modes two/three and shared status tail\n\nPartial/unaccepted;148 instruction bytes47FF26..47FFBA;prefix21486 supplies24frame,R4statusinitial0. Mode2freshwordthrough4801E0 bits2..7replaced32store;wordthrough4801E4=1;FFB4returnsR4zero. Mode3freshwordthrough48010Cclearbit24store;freshword480110clearbit0store;independentfreshsamepointerclearbits1..3store;word4801E8=0;word4801EC=0. SP0=1 overwrites savedentryR0;480826(5,literal4801E8pointer,0x3FFFFFFF,0,fifth1),fullnonzero→FFB6unchanged. ZeroSP8=0 overwrites savedentryR2;480312(3,0,SP+8,liveR3),returnignored. SP0=1;480826(5,literal4801ECpointer,1220,0,fifth1)fullresultR4;nonzeroR0=R4→FFB6;zeroSP4=0overwrites savedentryR1;480312(4,0,SP+4,liveR3),returnignored;FFB4R0=R4. InvalidmodefromprefixFFB2R4=6thenFFB4. AllnormalprefixpathsFFB4returnfullR4;earlyFFB6pathsretainR0. ADDSP16discards savedentryR0..R3/localhelperslots,POP R4,PC releases8,total24. No PRIMASKoperations; orderedpartialwritesremainonhelperfailure. No ownership/MMIO/C/freeze/fullcoverageclaim. AdjacentFFBA..FFBCzero2notincluded.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
