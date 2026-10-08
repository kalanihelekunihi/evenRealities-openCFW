from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x48306c;end=0x4830da
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
o=b/'analysis/review-isolated-P2-21313/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Reverse byte output with leading and trailing space callbacks\n\nPartial/unaccepted;110 instructionbytes48306C..4830DA. PUSH{R3,R4,R5,R6,R7,R8,R9,R10,R11,LR}40bytes;R5=callbackentryR0,R6=entryR1,R7=entryR2position,R8=entryR3. FreshSP44→R4length(sixthargument),SP48→R9width(seventh),SP52→R10flags(eighth);SP40 fifthargumentbuffer remainsfreshloadedperbyte. StoreinitialR7SP0overwritessavedR3. If(flags&3)==0,R11=R4;whileunsignedR11<R9:BLXcallback(R0=32,R1=R6,R2=R7,R3=R8),ignoreinterpretedreturn;R7++,R11++mod. Otherflags skipprepadding.\n\nBodywhilefullR4!=0:decrementR4mod,R3=R8,R2=R7,R1=R6;freshwordSP40→R0buffer,freshbyte[buffer+R4]→R0;BLXR5;R7++mod;repeat. Thusreversebyteorderandfullwrappingcount,not signedlengthguard. AfterbodyR10LSL30 sign testsbit1;clearreturn;settrailingloop: freshSP0initialposition→R0;R0=R7-R0mod;unsignedR0<R9→callback(32,R6,R7,R8),R7++andretest;elseend. ReturnR0=currentR7;POP{R1,R4,R5,R6,R7,R8,R9,R10,R11,PC}40bytes,R1=storedinitialpositionSP0. No callbackstatuscheck/nullguard;preservefreshbuffer/initialpositionreads and exactflags. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
