from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47e878;end=0x47e8f2
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
o=b/'analysis/review-isolated-P2-20995/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Infinite callback driver and wrapping comparison dispatch\n\nPartial/unaccepted;122instructionbytes47E878..47E8F2,twoentries.\nE878 PUSH R7,LR8 once;infinite loop47E8F2(SP,liveargs),thenfreshSP0→R1;47E88C(fullreturnR0,R1,liveR2,R3);47E97A(liveargs);branchE87A. Noepilogue/return or repeatedframegrowth;SP0initialsavedentryR7 exposedtohelperwrites. Confirms21384addressE879ThumbentryE878.\nE88C PUSH R2,R3,R4,R5,R6,LR24;R5=entryR0,R4=entryR1;454D7C(liveargs);47E916(SP,liveargs)→R6fullresult. FreshSP0nonzero→454DCC(liveargs),return. FreshSP0zero: ifR4zeroANDunsignedR6>=R5→454DCC(liveargs),47E83A(entryR0,R6,liveargs),return. OtherwiseifR4nonzero: freshword[pointerliteralEB7C],thenfreshword[resultpointer];zero→R4=1,nonzero→R4=0. OriginalR4zero remainszeroonthispath. R5=(entryR0-R6)modulo2^32;442030(freshword[pointerEB6C],R5,R4,liveR3);454DCC(liveargs);fullreturnedR0zero→4420BC(liveargs),nonzero skips. ReturnPOP R0,R1,R4,R5,R6,PC24: R0=SP0,R1=SP4 (initiallysavedentryR2/R3,subject47E916andothercallee writes),not lasthelperresult. Preserve unsignedcomparisonandwrappingsubtraction, distinctcalls. No C/freeze/completenessclaim;helpersremainingunresolved.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
