from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47d71c;end=0x47d7b6
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
o=b/'analysis/review-isolated-P2-20895/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Selector five three fresh helper observations conditional message\n\nPartial/unaccepted;154instructionbytes;inherited40frame,R5buffer,R4zero. D71Cquery43D0CEbit1zero→D738;elseSP4=literal47D99C,SP0=229;43D574(3,literal47D918,literal47D914,literal47D910,229,literal47D99C). D738freshquerybit0one→D748;elseanotherquerybit2zero→D754;D74843CE9E(0x0C000000,literal47D9A0,same,liveR3).\nD754call45A568withliveargs;thenfreshbyte[R5+5]compareLOW8result;unequal→D7B4. EqualD760querybit1zero→D784;else4A2914(liveargs),LOW8result→SP8,literal47D9A4→SP4,231→SP0;43D574(4,literal47D918,literal47D914,literal47D910,231,literal47D9A4,LOW8helperResult).\nD784freshquerybit0one→D794;elseanotherquerybit2zero→D7A8;D794independently4A2914(liveargs);LOW8result→R3;43CE9E(0x10400000,literal47D9A8,same,LOW8independentResult).\nD7A8independently4A2914(liveargs);comparefullresultzero;zero→D7B4;nonzero→47CED6(liveargs). D7B4branchpendingD7B6. R4notassigned. Preserveuptothreeseparatehelperobservations,diagnosticLOW8vsfunctionalfullresult. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
