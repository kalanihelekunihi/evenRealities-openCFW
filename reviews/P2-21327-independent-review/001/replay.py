from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4832dc;end=0x48334e
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
o=b/'analysis/review-isolated-P2-21327/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Wide radix digit loop and numeric output handoff\n\nPartial/unaccepted;114 instructionbytes4832DC..48334E,continues48329C104-byteframe. EntryhelperreturnedR2rawdigit;R0=oldR9count,R9=R0+1mod;R1=UXTB(R2),signedbytecompare10. Lowbyte<10R2+=48mod;elseflagsR8bit5 chooses65or97 inR1,R2+=R1then-=10mod. R1=SP28,storelowbyteR2[buffer+oldcountR0]. Call47CC60(R0=R4,R1=R5,R2=R6,R3=R7);returnedR0/R1→R4/R5. Fullpairzero→483320;elseunsignedR9<32→4832D0firsthelpercall,repeatremainderflow;otherwise483320. Helpersemanticcontractunresolved;noteTWOcallsoncurrentpairperiteration,firstR2consumedthen secondR0/R1retained.\n\nCommon483320 R3=R10,R2=R11;freshSP64context→R1,SP60callback→R0;storeR8flagsSP24;freshSP132→R4→SP20;freshSP128→R4→SP16;R6lowradixword→SP12;freshbyteSP112→R4→SP8fullword;R9count→SP4;R4=SP28buffer→SP0;call4830DA. RetainR0;ADDSP68bypasses60localsandtwo savedentryR0/R1slots;POP{R4,R5,R6,R7,R8,R9,R10,R11,PC}36bytes,total104released. Following48334E..350zeroexcluded. Preservefreshread/storeorder,lowradixwordhandoff andentryposition/contextrestoration. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
