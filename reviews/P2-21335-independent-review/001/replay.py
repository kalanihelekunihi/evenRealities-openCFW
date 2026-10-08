from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x48348c;end=0x4834fc
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
o=b/'analysis/review-isolated-P2-21335/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Fraction rounding carry and half-comparison parity branches\n\nPartial/unaccepted;112 instructionbytes48348C..4834FC,continues48335080-byteframe. FirstentryR4++mod;VMOVs2,R4;VCVT.f64.u32d1,s2;R9+=R7<<3mod;VLDRd2eightbytes[R9];VCMPd1,d2/VMRS;LT→4834C8,elseR4=0,R5++mod,branch4834C8. Separate4834AE immediateVMOV.f64d3,#96(0.5);VCMPd1,d3/VMRS;MI→4834C8. OtherwiseifR4==0incrementR4;nonzeroR4LSL31signbit0clear→skip,bit0setincrementR4. Do not silentlyreplaceFPconditionbrancheswithstandardroundingalgorithm.\n\nCommon4834C8 R7!=0→unresolved4834FC. Zero precision:VMOVs2,R5;VCVT.f64.s32d1,s2;VSUBd0=d0-d1;VMOV.f64d2,#96(0.5);VCMPd0,d2/VMRS;PL→4834F4. MIpathVLDRd2eightbytes483644;VCMPd0,d2/VMRS;LT→unresolved48355C,else4834F4. R5LSL31bit0clear→48355C;setR5++modthen48355C. PreservedifferentLT/MI/PLFPconditions,currentd0mutation,tablepointerR9overwrite,full32-bitcarry/parity and8byteconstantobligation. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
