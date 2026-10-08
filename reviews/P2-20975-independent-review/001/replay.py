from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47e4a6;end=0x47e51c
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-two-byte-helper-low-byte-message-diagnostics-21374-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Two-byte message with helper low byte and independent diagnostics\n\nPartial/unaccepted;118instructionbytes47E4A6..47E51C. PUSH R3,R4,R5,LR16;SP-=16,total32.4A7832(liveargs)→R4fullresult. R5=SP+12;43C0E4(SP+12,2,0,liveR3),thenexplicitbyteSP12=13,SP13=LOW8R4. SP0=5;465480(16,SP+12,2,0)withfifthstackarg5. Sendresultignoredbyfollowingcalls.\nFirstfresh43D0CEbit1set→SP8=LOW8R4,SP4=literalE650,SP0=127;43D574(4,literalE624,literalE620,literalE654),stackargsretained. Thenindependentfresh43D0CEbit0set→masklogger;elseanotherfresh43D0CEbit2set→masklogger. Masklogger43CE9E(10400000hex,literalE658,literalE658,LOW8R4). NoforcedR0return:liveR0fromlastflaghelperormasklogger. SP+=20discards16localsandsavedentryR3;POP R4,R5,PC12. No failurecheck/retryonsend; separateobservationsmustnotcache. Payloadinitialhelpersemanticsnotneededforexplicit2bytes,butcalleewritespossible. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
