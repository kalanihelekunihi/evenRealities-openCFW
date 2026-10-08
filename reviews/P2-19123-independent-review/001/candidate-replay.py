from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4698ee;end=0x46997c
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selector3-payload255-guard-global-action-flag-clear-and-zero-exit-19524-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Selector-three path 0x4698EE..0x46997C\n\nPartial/unaccepted;142instructionbytes. Inherit32frame, entryfromFULLoriginalR0!=2; liveR0originalselector,R1originalarg1,R2originalarg2,R5originalR3. FULLR0!=3 branches46997C. FULLR1zero orFULLR2zero eachbranches469978. Otherwise unsignedbyte[R1] ->R0; explicitUXTB thenFULLcompare255; unequalbranches469978.\n\nFresh43D0CE bit1 diagnostic SP4literal469BC0,SP0=335,R3literal469B90,R2literal469B38,R1literal469B3C,R0=4 ->43D574. Separatefreshbit0 orconditionalthirdfreshbit2 R1literal469BC4,R2R1,R0=0x10000000,liveR3 ->43CE9E.\n\nR2=literal469B9C,R0=freshword[R2];FULLzero branches469978. Nonzero R1=266,R0=SECONDfreshword[R2] ->4641B6 withliveR2/R3. R0=0,R1literal469B44,storebyte0[R1];call45A568(liveargs). FULLresult!=1 branches469978. FULL1 freshunsignedbyte[addressliteral469B88] ->R0; nonzero branches469978. Zero setsR0=0 ->49BF24(liveargs); then45A8EE(1,0,0,500).469978explicitR0=0 ->469ADE outsidechunk. Preservetwofreshglobalwordreads andorderedchildsideeffects. No C,freezeorchildcontractclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
