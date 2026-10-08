from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x483424;end=0x48348c
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
o=b/'analysis/review-isolated-P2-21333/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Floating precision cap, integer and fractional scaling\n\nPartial/unaccepted;104 instructionbytes483424..48348C,continues48335080-byteframe. FlagsR12bit10clear→R7=6defaultprecision;setretainsR7. LoopunsignedR8<32 andunsignedR7>=10: R4=48,R5=SP16buffer,storelowbyte[R5+R8],R8++mod,R7--mod;repeat. Thuswriteszeroswhileprecision>=10butnootherprecisionclampwhenbufferfull.\n\nVCVT.s32.f64 s2,d0;VMOVR5,s2(integerbits). Freshliteral484000→R9tablepointer. VMOVs2,R5;VCVT.f64.s32d1,s2;VSUBd1=d0-d1. R4=R9+(R7<<3)mod;VLDRd2eightbytes[R4];VMULd1=d1*d2;VCVT.u32.f64s4,d1;VMOVR4,s4(fractionintegerbits);VMOVs4,R4;VCVT.f64.u32d2,s4;VSUBd1=d1-d2. VLDRd3eightbytesliteral483644;VCMPd1,d3;VMRSAPSR;LT(N!=V)→unresolved4834AE,elsefallthrough48348C. PreservehardwareFPconversion/FPSCRsemanticswithoutassuminghostrounding,signedintegerconversionversusunsignedfractionconversion,indexwrappingand8byteconstant/tableobligations. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
