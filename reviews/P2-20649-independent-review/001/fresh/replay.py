from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47a71c;end=0x47a798
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
o=Path('reviews/P2-20649-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Count five entry diagnostic prefix\n\nPartial/unaccepted; 124 instruction bytes, routine prefix. PUSH R0,R1,R2,R3,R4,R5,R6,R7,R8,LR creates 40-byte frame. R7=full entry R0, R8=full entry R1, R5=full entry R2, R6=literal47AE64. Saved R0..R3 slots SP0..12 are writable scratch and later discarded, not return slots.\nCall recovered 0x47A676(LOW8 R5, live remaining arguments); signed R0<5 branches to pending0x47A7B6. Otherwise query0x43D0CE with live arguments; status bit1 zero skips to0x47A76C. Bit1 set selects literal47A8A4 for LOW8 R5 nonzero or47A8A8 for zero, writes selection SP8, literal47AE68 SP4, 918 SP0; call0x43D574(4,literal47AE28,literal47ADCC,literal47AE6C,fifth918,sixthliteral47AE68,seventhselection).\nAt0x47A76C query status afresh; bit0 one enters0x47A77C; otherwise query again and bit2 zero branches0x47A798. Mask path independently selects literal47A8A4/47A8A8 using LOW8 R5 without narrowing R5, loads R1=literal47AE70,R2=R1,R3=selectedliteral and calls0x43CE9E(0x10400000,R1,R2,R3). Fallthrough pending0x47A798. Preserve all separate queries and live arguments. No C, freeze or wholecoverage claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
