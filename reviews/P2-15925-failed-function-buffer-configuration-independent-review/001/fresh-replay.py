from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x5401fe;end=0x540264
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
o=Path('reviews/P2-15925-failed-function-buffer-configuration-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Buffer configuration continuation, 0x5401FE..0x540264\n\nPartial; accepted:false.102bytes continuation of540036 candidate; frame224 active. After prioracquiresuccess:\n\nword[SP+8]=0;word[SP+4]=FFFFFFFF;word[SP+0]=8\nR0=word[SP+76];R0=word[R0+64];R3=word[R0+4]>>16\nR0=freshword[SP+76];R0=word[R0+64];R2=UXTH(word[R0+4])\nR0=freshword[SP+76];R0=word[R0+64];R1=word[R0+16]\nR0=1;call4B1298()\nword[SP+8]=0;word[SP+4]=FFFFFFFF;word[SP+0]=8\nR3=R9;R2=R9;R1=word[SP+88];R0=2;call4B1298()\nword[SP+4]=0;word[SP+0]=FFFFFFFF\nR3=2;R2=1;R1=1;R0=word[SP+76];call4B06C0()\nR3=word[SP+164];R2=word[SP+108];R1=0;R0=0;call4B1516()\ncontinue540264\n\nStackwords are actual call-context memory; child prototypes/additionalargument consumption remain unresolved. Registers and stackargs explicitly refreshed at shownsites, including three separatepointerchains for firstcall dimensions/backingptr. Child R0results discarded by following overwrite; child memoryeffects not assumedabsent. No completefunction behavior/ABI, C/admission/gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
