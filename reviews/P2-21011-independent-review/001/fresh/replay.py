from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47ebf8;end=0x47ec6a
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
o=b/'analysis/review-isolated-P2-21011/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text("# Object operation entry guards and caller fifth argument\n\nPartial/unaccepted;114instructionbytes47EBF8..47EC6A,entryprefixonly;remainingroutineunrecovered. PUSH R4,R5,R6,R7,R8,R9,R10,LR32;R4=entryR2,R7=entryR3,R8=entryR0,R9=0,R2=0. FullentryR0zero→5FA0A4(liveargs),ifreturnsstore0toFFFFFFFFthenEC18selfloopifstorecompletes. Nonzero→R6=fullentryR1;TST R6,FF000000:nonzero→samefatalwrite/selfloopEC2E. Highbytezero→fullR6zero→samefatalwrite/selfloopEC40. Thusordinarysurvivingmask1..FFFFFF,notLOW8conversion.\nR5=freshSP32caller'sfifthstackarg;4558A4(liveargs). Fullhelperresultnonzero→temporaryboolean1;fullzeroANDfullR5zero→1;fullzeroANDR5nonzero→0. UXTBbooleanthenzerotest;zero→fatalcall/write/selfloopEC68. SurvivingconditionhelpernonzeroORcallerfifthargzero,not helper==2. ContinueEC6AwithR4entryR2,R7entryR3,R8objectpointer,R6entryR1,R5fiftharg,R9zero;frame32remainsactive. Externalhelperregisterclobbers subjectABI, no return/wholefunctionsemanticsclaimed. No C/freeze/completenessclaim.\n")
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
