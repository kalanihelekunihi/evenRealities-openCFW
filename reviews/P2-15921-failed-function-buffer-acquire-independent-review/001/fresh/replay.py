from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x5401b6;end=0x5401fe
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
o=Path('reviews/P2-15921-failed-function-buffer-acquire-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Mode bit, centers and buffer acquisition, 0x5401B6..0x5401FE\n\nPartial; accepted:false.72bytes continuation, frame224 active. Enteronly priorpointerSP88NZ. Ordered:\n\nR0=byte[R5+53]&1;byte[SP+80]=R0\nR0=SP+44;call451598()\nR1=word[SP+44];R2=2;R10=u32(SDIV(s32(R0),2)+R1)\nR0=SP+44;call4515A4()\nR1=word[SP+48];R2=2;R11=u32(SDIV(s32(R0),2)+R1)\nR2=word[SP+108];R1=freshword[SP+108];R0=word[SP+76];call4B0B5A()\nR0=UXTB(R0)\nif R0==1:continue5401FE\nR0=word[SP+88];call44F758()\nbranch5409BE // epilogue outside packet\n\nFreshSP108 reads into twoargs retained for aliases/ordering; SDIVtrunczero, adds wrap. Child4B0B5A lowbyte1 is onlysuccess value; upperbitsdiscarded. Failure calls44F758 with pointer, result ignoredbybranch; cleanup naming inferred, effects unresolved. Geometryhelpers451598/4515A4 existing10420 packet reused. No standaloneABI/return claim, C/admission/gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
