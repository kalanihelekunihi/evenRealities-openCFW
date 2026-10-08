from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x480c56;end=0x480d06
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
o=b/'analysis/review-isolated-P2-21151/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Priority-bit byte query and qualified fetched output prefix\n\nPartial/unaccepted;176 instruction bytes480C56..480D06. Separate frameless query480C56: pointerliteral480EC8 freshword bit8 set→byte[entryR0]=2;else SECOND freshword bit0 set→byte=1;elsebyte=0. Prioritybit8 andbit0 need not share snapshot. Return0 viaBXLR480C7A; no pointerguard.\n\nRoutine480C7C PUSH R2,R3,R4,LR16;R4entryR0 output. Call4D3F3C(R0=1,R1=580,R2=1,R3=SP). Immediately store0 tooutput12 before checking fullhelperR0;nonzero→480D3C unresolved failure path. Zero: R1pointerliteral480E7C;freshword bits4..7==2, then SECONDfreshword low4bits>=2 (signedBLT,values0..15), then wordSP0<255 unsigned;alltrue→R2bool1 otherwise0. If false→480D06 unresolved here. If true: THIRDfreshword low4bits==3 skips decrement,otherwise reloadSP0 subtract1mod2^32 storeSP0. Four separate output12 RMWs: BFIbits8..15=2;freshbyteSP0 BFIbits0..7;freshword OR0x20000;freshword OR0x10000. Branch480D70 unresolved continuation. Preserve fresh reads,helper output stackaliasing,and ordered stores; no collapse to singlepackedstore. Neither epilogue nor finalstatuscovered for480C7C. No C/freeze/fullcoverage/equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
