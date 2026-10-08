from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x481bb8;end=0x481c48
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
o=b/'analysis/review-isolated-P2-21209/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text("# Pointer zero extension and count-store policy/modifier dispatch\n\nPartial/unaccepted;144 instruction bytes481BB8..481C48. Continues481836232frame. Pointerconversion:loadargcursor[R9]→R1,loadwordpostincrement4→R0,storeadvancedcursor;R4=R0(BIC0),R1=0,R5=0(BICFFFFFFFF);STRD R4,R5→SP8/SP12 zeroextended64bitvalue. R3=SP72→SP20;R1='x'(120);branch482476 unresolvedintegerconversion.\n\nCountconversion481BDC:loadpointerSP172 thenbyte[pointer+1]policy;nonzero→R4FFFFFFFF,ADR R0=4826B4,branch481A4E existingdiagnostichelperpath. Zero:reloadmodifierbyteSP66,dispatchb98→481CB6,h104→481C28,j106→481C7C,l108→481C0E,q113→481C94,t116→481C62,z122→481C48,other→481CD4. Otherdestinationsunresolvedhere.\n\nModifierl:loadargcursor,freshpointerwordpostincrement4,storecursor;nonnull→481CEC unresolvedwordstore;null→R4FFFFFFFF,ADR R0=4826CC,branch481A4E. Modifierh:samepointerfetch/cursorupdate;null→sameADR4826CC diagnosticpath;nonnull→freshwordSP52counter,STRHlow16counter[targetpointer],branch4824AC. Policyrejectpathconsumesnoargument;nullargumentpathsadvancecursorbeforediagnostic. No inferredstandardprintfsemantics, C/freeze/fullcoverage/equality claim.\n")
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
