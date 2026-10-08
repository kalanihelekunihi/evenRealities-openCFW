from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47ac60;end=0x47acea
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
o=Path('reviews/P2-20685-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Indexed byte46 bit0 boolean return\n\nPartial/unaccepted;138 instructionbytes,inherited56-byteframe. Bit0setroute0x47AC60 queries0x43D0CE;statusbit1zero skips0x47AC82,otherwisewriteliteral47B590 SP4,1088 SP0;call0x43D574(4,literal47AE28,literal47ADCC,literal47B580,fifth1088,sixthliteral47B590). At0x47AC82queryfreshstatus;bit0oneenters0x47AC92,otherwisequeryagainandbit2zero skips0x47ACA0. MaskpathR1literal47B594,R2same,liveR3;call0x43CE9E(0x10000000,R1,R2,liveR3). ExplicitR0one,branchshared0x47ACE6.\nBit0clearroute0x47ACA4queriesstatus;bit1zero skips0x47ACC6,otherwisewriteliteral47B598 SP4,1097 SP0;call0x43D574(2,literal47AE28,literal47ADCC,literal47B580,fifth1097,sixthliteral47B598). At0x47ACC6queryfreshstatus;bit0oneenters0x47ACD6,otherwisequeryagainandbit2zero skips0x47ACE4. MaskpathR1literal47B6DC,R2same,liveR3;call0x43CE9E(0x08000000,R1,R2,liveR3). ExplicitR0zero.\nShared0x47ACE6addsSP40:discard36localsand savedentryR3slot,thenPOP R4,R5,R6,PC16bytes restoresremainingframeandreturns explicitR0one/zero. Entryinvalidguardroutealsojoinswithzero. Separatequeriesandliveargumentspreserved. No C,freezeorwholecoverageclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
