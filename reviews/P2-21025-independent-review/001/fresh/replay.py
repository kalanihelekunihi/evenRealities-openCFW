from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47ee60;end=0x47eefa
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
o=b/'analysis/review-isolated-P2-21025/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Three-helper reset sequence and constructed local record result\n\nPartial/unaccepted;154instructionbytes47EE60..47EEFA,twoentries.\nEE60 PUSH R7,LR8;4D3628(0,0,liveR2,R3);4D3CAE(0,liveR1,R2,R3);4D3ACC(liveargs);R0=0;POP R1,PC returnsR1=savedentryR7. Allhelperresultsdiscarded,alwayszeroifnormallyreturns.\nEE78 PUSH R4,LR8;SP-=48,total56;R4=entryR0recordpointer. Freshwordsrecord24/28/32→SP32/36/40;SP44=0. Freshword20→R2,word16→R1,word12+2000modulo2^32→R0;4D3CF8(R0,R1,R2,liveR3)→SP12fullresult. Independentlyfreshwords20/16/12→SP28/24/20;SP16=1. SP8notexplicitlyinitialized.4D3ADC(SP+8,liveR1,R2,R3). Fullzero→R0=0exit,no diagnostics. Fullnonzero→firstfresh43D0CEbit1set→SP4=literalEEFC,SP0=221;43D574(1,literalEF08,literalEF04,literalEF00). Thenfresh43D0CEbit0set→masklogger;elseanotherfreshcallbit2set→masklogger. Masklogger43CE9E(04000000hex,literalEF0C,literalEF0C,liveR3),R3notexplicitlyset. RegardlessdiagnosticsnonzeropathR0=1exit. SP+=48;POP R4,PC restoresentryR4. Distinctrecordobservationsbefore/afterhelperpreserved,no48bytememsetinferred. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
