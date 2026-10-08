from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x46997c;end=0x4699e0
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selector4-null-global-diagnostics-counter-increment-signed-threshold-19526-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Selector-four guard and counter 0x46997C..0x4699E0\n\nPartial/unaccepted;100instructionbytes. Inherited32frame,FULLoriginalselectorR0. FULLR0!=4 branches469A76. Equal4 loadsR0=literal469B9C thenfreshword[R0]; FULLnonzero branches4699C6. Zero fresh43D0CEbit1diagnostic:SP4literal469BC8,SP0=353,R3literal469B90,R2literal469B38,R1literal469B3C,R0=2 ->43D574. Separatefreshbit0 orconditional thirdfreshbit2: R1literal469BCC,R2R1,R0=0x08000000,live3 ->43CE9E. R0=0 ->469ADE.\n\nNonnull4699C6 R0=literal469B98;R1=freshword[R0+24];R1=wrapping32(R1+1);storeword[R0+24];SECONDfreshword[R0+24] ->R1; compareSIGNED32 R1 against180. Signedless branches469A72, includingnegativewrappedvalues. OtherwiseR1=0;storeword0[R0+24];call45A568 withR0globaladdress,R1zero,liveR2/3. FULLresult!=1 branches469A72;FULL1 falls4699E0 outsidechunk. Preservewrite-then-freshread andsignedthreshold; no unsignedcounterreplacement. No C,freezeorchildcontractclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
