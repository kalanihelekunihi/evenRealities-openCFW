from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47d35c;end=0x47d3d4
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
o=b/'analysis/review-isolated-P2-20881/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Selector two first match set bit two asymmetric result compare\n\nPartial/unaccepted;120instructionbytes;inherited40frame,R5buffer,R6fullprior47D8CEresult,R4zero.\nD35C call45A568withliveargs;thenfreshunsignedbyte[R5+4];comparetoLOW8helperresult. Unequal→pendingD43C. EqualD368query43D0CEbit1zero→D390;elsefreshbyte6→SP8,literal47D96C→SP4,126→SP0;43D574(4,literal47D918,literal47D914,literal47D910,126,literal47D96C,freshByte6).\nD390freshquerybit0one→D3A0;elseanotherquerybit2zero→D3B0. D3A0independentlyfreshbyte6→R3;43CE9E(0x10400000,literal47D970,same,freshByte6).\nD3B0independentlyfreshbyte6==1:ptrliteral47D900;freshflagbyteOR4store. Thenindependentlycall47D8CEwithliveargs;R6=LOW8priorR6;compareR6againstfullnewR0. UnequalR4=1→pendingD514;equalR4=0→pendingD514. Newhelperresultisnotnarrowed; oldresultnarrowedonlyaftercall. Byte6not1→pendingD3D4,whereanotherfreshreadoccursoutside map.\nDo notassumehelperstableorflagupdateeffects. Diagnosticstackwriteslocal; no C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
