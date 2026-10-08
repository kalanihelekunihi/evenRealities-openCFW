from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47d870;end=0x47d8ce
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
o=b/'analysis/review-isolated-P2-20907/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Entry low-byte boolean message builder bit-zero-one leaves\n\nPartial/unaccepted;94instructionbytes,threeentries. D870PUSH R2,R3,R4,LR16;R4=fullentryR0. Loadpointerliteral47D9C0;LDRD R2,R3,[pointer];STRD toSP0/SP4overwrites savedR2/R3with8templatebytes. Call45A568withliveargs;LOW8result→SP4. Independentlycall45A568againwithliveargs;fullresult==1→SP5=2;elseSP5=1.\nR4=LOW8entryR0;zero→SP6=0;nonzero→SP6=1. ThusentryR0=256 produceszero. SP0..3andSP7retaintemplatebeforecallee. Call464D1C(259,SP,8,0),distinctfromprevious4651E0. POP R0,R1,R4,PC16 returnsR0=templatewordSP0,R1=modifiedwordSP4(bothsubjecttocallee memorywrites),R4=savedentryR4. CallresultR0discarded.\nD8B8separateleafentry:loadliteral47D900pointer;freshunsignedbyte;AND1→R0;BXLR. D8C2separateleafentry:samepointer,freshunsignedbyte;extractbit1;UXTB;BXLR. Bothfull0or1,R1/R2/R3untouched,no frame/no fallthroughbetweenentries. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
