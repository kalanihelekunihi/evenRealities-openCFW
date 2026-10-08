from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47b8ce;end=0x47b932
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
o=Path('reviews/P2-20763-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Byte46 mismatch fresh observations clear flag\n\nPartial/unaccepted;100instructionbytes,inherited40-byteframe,R5entryrecord,R4matchedtablepointer,R6inheritedflag. Freshbyte[R5+46]R0thenfreshbyte[R4+46]R1;equalbranches0x47B932preservingR6. Unequalquery43D0CE;bit1zero skips0x47B908;otherwisefreshbyte[R4+46]SP12thenfreshbyte[R5+46]SP8,literal47C298 SP4,1939 SP0;call43D574(1,literal47BC24,literal47BC20,literal47C27C,fifth1939,sixthliteral47C298,seventhfreshentrybyte46,eighthfreshtablebyte46).\nAt0x47B908queryfreshstatus;bit0oneenters0x47B918,otherwisequeryagainandbit2zero skips0x47B930. MaskpathR1literal47C29C,freshbyte[R4+46]SP0thenfreshbyte[R5+46]R3,R2sameR1;call43CE9E(0x04800000,R1,R2,freshentrybyte46,fifthfreshtablebyte46). At0x47B930R6zeroevenifdiagnosticsdisabled. Fallthroughpending0x47B932. Comparison/logger/maskreadpairsareindependentandordered;stackwritesaliasSP0..12savedentryR0..R3;maskoverwritesSP0withtablebyte46. No C,freezeorcompletenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
