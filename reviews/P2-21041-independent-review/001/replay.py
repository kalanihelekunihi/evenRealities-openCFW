from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47f204;end=0x47f294
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-byte-record-two-mask-prefix-conditional-bit-set-21440-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Byte record to two masks; conditional bit-zero setup prefix\n\nPartial/unaccepted;144instructionbytes47F204..47F294,prefixonly. PUSH R1,R2,R3,R4,R5,R6,R7,R8,R9,LR40;R4=entryR0pointer;no nullguardbeforeloads. SP4=0 overwrites savedentryR2;R6=0;R5=0. Freshbyte[R4+0] stored through literalFAD0pointer, then independently reload byte[R4+0]. Secondreadzero setsR6|=32,SP4|=128;allotherbytevalues addneither (byte1branchconvergeswithothers).\n\nFreshbyte[R4+1]&7 ORintoR6; independently freshbyte[R4+1]&7 ORintoSP4, so masks maydiffer ifrecordchanges. Freshbyte[R4+3]:1→R6|=8,SP4|=8;3→R6|=24,SP4|=72;0/others addneither. Independentlyfreshbyte[R4+3]==3 then freshword through literalFAD4 &72 equals8→independentfreshword through literalFAD8 OR1 stored, R5=1; otherwiseR5 remains0. This setup can occur even when earlier byte3 read chose anothermaskbranch. No read/handling ofbyte2inprefix. ContinueF294with40frameactive,R4input,R6mask,SP4othermask,R5setupindicator. No return/fullfunction claim; unresolvedpointedownership/externalbehavior, noMMIO/C/freeze/fullcoverage claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
