from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x460910;end=0x460970
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
o=Path('/tmp/p2-18509-fresh');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Mismatch exit and matched record prefix460910..460970\nPartial;unaccepted.96 instructionbytes,inherits64frame,R4headerbyte1,R5payloadbaseR7oldbuffer+4. Mismatch460910:R1=1,R0=low8retainedR4;4604C2 liveR2/R3;ignorechildresult,R0=FFFFFFFF→460D56externalepilogue.\nMatch460920:46018E liveR0/R1/R2/R3 withNOargumentreset;R1=1040,R2=0,R6=wordliteral46136C,R7=R6,R0=R7;43C0E4 liveR3. R7=0 REPLACESbufferaliaswithindex;branch460B02externaltest,whichmustprovideR9source stridebeforebody.\nBodyentry46093A:R8=52. R0=wrap32(R5+low32(R9*R7));R0=freshword[R0+48];R1=wrap32(R6+low32(R8*R7));word[R1+48]=R0. R0=4094;R1=SEPARATEcomputedR6+52*R7;word[R1+36]=4094. R0=1;R1=SEPARATEcomputedR6+52*R7;byte[R1+40]=1. R0=wordliteral461370;R1=low32(R8*R7);word[wrap32(R6+R1)]=R0. Orderedwriteskey48,defaultword36,defaultbyte40,word0. Freshsourcereadanddestinationaliasingretained;R8deststride,R9source-stridecontractunresolveduntiltestmapped. Next460970string/fieldchildcontinuationexcluded. No boundsinbody;externaltestcontrolsentry. Childcontracts unresolved.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
