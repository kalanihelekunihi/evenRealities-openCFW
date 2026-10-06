from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4b1350;end=0x4b1378
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
o=b/'reviews/P2-16003-graphics-buffer-layout-stride-dispatch-16400-independent-review/001/fresh/outputs';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Stride dispatch arms, 0x4B1350..0x4B1378,40 bytes\n4B1350: R6=u32(R6+(R6<<1)); branch4B13D0\n4B1356: R6=u32(R6<<1); branch4B13D0\n4B135A: R6=u32(R6<<2); branch4B1360\n4B135E: R6=u32(R6<<1)\n4B1360:\nR6=u32(R6+7); R1=ASR32(R6,2); R6=u32(R6+(R1>>29)); R6=ASR32(R6,3); branch4B13D0\n4B136C:\nR2=4; R1=u32(R1-4)\nif R1>74 unsigned: branch4B13CE\nTBB: branch u32(0x4B1378+2*byte[0x4B1378+R1])\n\n40byteactiveframeinherited. All branchentriesretained. Secondtable75bytes1378..13C3, plusoneexcludedbyte13C3..13C4 notclaimedinstruction. Arithmeticrightshiftandlogicalcorrections preserved.\n\nPartial; accepted:false. Wrapped32 arithmetic and original ordered loads/stores retained. Opaquechildren/architecturefaults/concurrency/ownership conditional, no formalcompletecontract, C, admission or gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
