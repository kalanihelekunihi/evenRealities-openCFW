from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x5144ba;end=0x5144fa
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
o=b/'/private/tmp/independent-ring-map-2';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Current buffer detach, 0x5144BA..0x5144FA,64 bytes\nPUSH R4,R5 (noLRsave)8\nR0=word[0x514B78]; R1=word[R0]; R0=word[R1+4]\nif R0==0: goto5144F2\nR2=word[R0+20]; R3=word[R0+16]; R4=u32(R2+2)\nif s32(R3)>=s32(R4):\n R3=word[R0+8]; R4=327680; R5=0\n word[R3+(R2<<2)]=R4; R3=u32(R3+4); word[R3+(R2<<2)]=R5\n R2=freshword[R0+24]&FFFFFFF7; word[R0+24]=R2\nR2=freshword[R0+24]&FFFFFFDF; word[R0+24]=R2\n5144F2: R0=0; word[R1+4]=R0; restoreR4,R5; SP+=8; returnviaLR\n\nMarkerpair50000,0 maybewrittenwithoutcursoradvance. Capacitysignedwrappedindex+2. Bit3onlyclearwhenmarkerwritten; bit5alwaysclearifbufferexists; contextcurrentpointeralwayscleared. ArgumententryR0ignored, globalcurrentused. GlobalwordR1retainedthroughwrites; aliaswithcontext/backingmayaffecteffectoflaststore. No calls/traps; normalreturn0, LRunchanged.\n\nPartial; accepted:false. Ordered instructions, wrap32 and signedconditions retained; childcontracts, architecturalfault/alias/concurrentstate/lifetime conditional. No C, admission, freeze, gate or physicalqualification.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
