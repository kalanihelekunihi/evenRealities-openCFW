from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x46928c;end=0x46931c
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-mode-one-two-predicate-action-paths-and-conditional-delay-19490-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Predicate action paths 0x46928C..0x46931C\n\nPartial/unaccepted;144 instruction bytes. Inherit32-byte frame and R5 saved context bool. Fresh0x43D0CE bit1 diagnostic: SP4=literal469B58, SP0=99, R3=literal469B4C, R2=literal469B38, R1=literal469B3C, R0=3 ->43D574. Independent freshbit0 or conditional third freshbit2: R2=literal469B5C, R1=R2, R0=0x0C000000, liveR3 ->43CE9E.\n\nAt4692CE call45A568 withliveargs; FULL result!=1 branches46931C. FULL1 setsR4=0 then calls44349C withliveargs. FULLresult1 setsR4=1 and calls464C36(0,0,0,0); otherwise skips first action. Bothpaths call4434B4 withrespective liveargs. FULLresult!=1 branches46931C. FULL1 andR4==0 calls464C36(0,0,0,0) then branches46931C. FULL1 andR4!=0 setsR0=500 andcalls454B4C withliveR1/R2/R3, then464C36(0,0,0,0). Fallthrough46931C.\n\nThus two full-one predicates can produce two ordered action calls, with child454B4C between them on the R4=1 path. No delay contract presumed fromconstant500; retain raw call. R4flag/R5bool and unchanged savedinputSP16 remain live for nextchunk. Freshread/call order preserved; no C, gate or runtimeclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
