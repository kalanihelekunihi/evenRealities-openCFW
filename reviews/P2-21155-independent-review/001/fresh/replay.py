from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x480d72;end=0x480e6c
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
o=b/'analysis/review-isolated-P2-21155/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Two-mode fresh bit-field byte output query\n\nPartial/unaccepted;250 instruction bytes480D72..480E6C. PUSH R7,LR8. FullentryR1 null→return6. NonnullR2=entryR1;selectorUXTBentryR0:0→decode,1→snapshot,other→return6 withoutoutputwrites. Mode0:R0=pointerliteral480E84;freshword low2bits index. Ordered byte writes offsets1,0,2: index0 values0,0,0;index1 values0,0,1;index2 values1,1,1;index3 values1,1,2. Mask guarantees0..3; nominal unmatchedbranch480DA0→480DD8 unreachableforstableinstructionsemantics.\n\nThen independentfreshwordreads fromsamepointer for each output:bits2..3→byte3;bit6→byte4;bit7→byte5;bit8→byte6;bit9→byte7;bit10→byte8;bit19→byte9;bits20..21→byte10. One-bit paths signedcompare<1 map0/1 exactly;never merge fresh reads or reorderstores,includingaliasing. R0=R2output;call480C7C withliveR1/R2/R3;ignorefullhelperresult;return0. Mode1:R0=R1entrypointer;call480874 withliveR1/R2/R3;ignorefullresult;return0. CommonPOP R1,PC releases8;R1restoressavedentryR7 unlesshelperaliasmutation. No sizeguard or outputinitializationoninvalidselector;padding480E6C..480E70zero4excluded. No C/freeze/fullcoverage/equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
