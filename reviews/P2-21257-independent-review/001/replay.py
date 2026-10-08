from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x482684;end=0x4826b2
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
o=b/'analysis/review-isolated-P2-21257/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Callback byte loop with state, counter and failure return\n\nPartial/unaccepted;46 instructionbytes482684..4826B2. PUSH{R3,R4,R5,R6,R7,LR}24-byteframe. R5=entryR0 callback,R6=entryR1 structure,R7=entryR2 source,R4=entryR3 count; R0=0. If fullcountzero skipallreads/calls and return0 viaPOP{R1,R4,R5,R6,R7,PC};returnedR1=savedentryR3.\n\nLoop: freshbyte[R7]→R1 withsourcepostincrement1; then freshword[R6+8]→R0; BLX R5 withtheseR0/R1 and liveR2/R3. Store fullreturnedR0 to[R6+8] before testingzero. Zero→errorentry4826AC setsR0=FFFFFFFF andsamePOP, no counterincrement. Nonzero: freshword[R6+44]→R0,incrementmod2^32,storeback; R0=0;decrementR4mod2^32 and repeatifnonzero. Thus successfulreturn0; fullunsignednonzerocount controls wrapping decrement withoutsignedguard. Callbackeffects may affect subsequently fresh state/counterreads; sourceisadvanced beforecallbackfailure. No callbackvalidityguard, no assumed externalbehavior. Following4826B2..B4 zerohalfword excluded;4826B4+diagnosticstrings are data outsidecandidate. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
