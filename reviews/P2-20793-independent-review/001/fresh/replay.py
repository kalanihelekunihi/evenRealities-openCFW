from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47bec8;end=0x47bf2e
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
o=Path('reviews/P2-20793-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Eligible record seven byte mask two fresh extrema reloads\n\nPartial/unaccepted;102instructionbytes,inherited72-byteframe,R10recordpointer,R9fullindex,R5thresholdinitializedFFFFFFFF,R6thresholdinitializedzero,R7/R8indexesinitializedzero. At0x47BEC8query43D0CE;bit0oneenters0x47BED8,otherwisequeryagainandbit2zero skips0x47BF0E. MaskpathR1literal47C8C0;freshbyte[R10+6]SP20,thenfreshbytes0..4ascendingintoSP16,12,8,4,0;freshbyte5R3,R2sameR1;call43CE9E(0x11C00000,R1,R2,byte5,fifthbyte4,sixthbyte3,seventhbyte2,eighthbyte1,ninthbyte0,tenthbyte6). Theseobservationsindependentfromlogger2023.\nAt0x47BF0Efreshfullword[R10+196]R0compareunsignedR0>=R5;greaterorequalskip0x47BF1C. Otherwiseindependentlyfreshreloadword196intoR5andR7=fullR9. At0x47BF1Cindependentlyfreshword196R0compareunsignedR6>=R0;greaterorequalbranchesrecovered0x47BDEElooptail. Otherwiseindependentlyfreshreloadword196intoR6andR8=fullR9,thenbranchsametail. Fourpossiblewordreadsnotcached;thresholdupdatesmaynotreflectcomparisonobservations,nomonotonicityassumed. Onlyeligiblebothguard-nonzeropathreachesthesecomparisons;alltenrecordsprocessedviatail. No C,freezeorcompletenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
