from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x540264;end=0x5402c8
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
o=Path('reviews/P2-15927-failed-function-first-region-clip-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# First region clip continuation, 0x540264..0x5402C8\n\nPartial; accepted:false.100bytes continuation, frame224active. Ordered wrapped expressions and childcalls:\n\nword[SP+20]=word[SP+52]\nR0=freshword[SP+52];R0=u32(R0-R9);R0=u32(R0+1);word[SP+12]=R0\nword[SP+16]=word[SP+48]\nR0=freshword[SP+48];R0=u32(R9+R0);R0=u32(R0-1);word[SP+24]=R0\nR1=SP+12;R0=SP+60;call540024()\nR0=word[SP+12]\nif s32(R10)<s32(R0):R0=freshword[SP+12]\nelse:R0=R10\nword[SP+60]=R0\nR0=word[SP+24]\nif s32(R0)<s32(R11):R0=freshword[SP+24]\nelse:R0=R11\nword[SP+72]=R0\nR2=u32(R4+56);R1=SP+60;R0=SP+28;call450BCC()\nif R0==0:branch540308\nR2=R8;R1=SP+92;R0=SP+28;call450F28()\nif R0!=0:branch540308\nR0=SP+112;call561810()\ncontinue5402C8\n\nMax/min comparisons signed; repeatedloadsaftercompare retained, not collapsed into immutableminmax. Copy/clipping/geometry initialization names inference only; opaque childmemoryeffects and exactcontracts unresolved. Both skipbranches joinoutsidepacket at540308. No fullfunction return/ABI or physicaldrawing/alias/fault/concurrency qualification, no C/gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
