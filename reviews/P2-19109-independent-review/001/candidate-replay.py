from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x469580;end=0x4695fe
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-selector2-entry-global-flag-set-buffer-child-and-byte-guard-19510-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Selector-two entry 0x469580..0x4695FE\n\nPartial/unaccepted;126instructionbytes. PUSH R0/R1/R2/R3/R4/R5/R6/LR creates32-byteframe; SP0/4/8/12 originalargs,SP16/20/24 saved4/5/6,SP28LR. R5=originalR3. FULLR0!=2 branches4698EE. Equal2 fresh43D0CE bit1 diagnosticloadsunsignedbyte[addressliteral469B88] ->SP8, literal469B8CSP4,214SP0,R3literal469B90,R2literal469B38,R1literal469B3C,R0=3 ->43D574.\n\nSeparatefreshbit0 orconditional thirdfreshbit2 enables R1=literal469B94, independentlyfreshunsignedbyte[addressliteral469B88] ->R3,R2=R1,R0=0x0C400000 ->43CE9E. At4695DA setR0=1,R1=literal469B44,storebyte1[R1]. R1=28,R2=0,R4=literal469B98,R6=R4,R0=R6 ->43C0E4 withliveR3; nofillcontractpresumed. Freshunsignedbyte[addressliteral469B88] ->R0; bytezero branches4697BA,nonzero continues4695FE. R4globaladdress,R6sameaddress,R5originalR3remainlive. SP0/4/8 maydiagnosticoverwriteoriginalargs. No C,freezeorchildsemanticclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
