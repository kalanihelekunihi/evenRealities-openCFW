from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4807a0;end=0x4807f0
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
o=b/'analysis/review-isolated-P2-21129/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Floating conversion threshold and external low-address call\n\nPartial/unaccepted;80 instruction bytes4807A0..4807F0. PUSH R7,LR8. VMOV entryR0rawbits→S0;VCVT.F32.U32 convertsunsignedinteger tofloat32;VCVT.U32.F32 S0,S0,#5 convertsfloat32to unsignedfixed-pointwith5fractionbits (retainarchitecturalconversion/rounding/saturation/FPSCR behavior,not simplewrappingentry*32). VMOVresultbits→R0. Freshwordthroughliteral4807F8 bits3..4!=2 setsR1=15. Equal2 convertscurrentR0unsignedtofloat32 S0,loadsS1floatbitsliteral4807F0;VMUL.F32 S0,S0,S1;loadsS1literal4807F4;VDIV.F32 S0,S0,S1;VCVT.U32.F32 S0,S0;VMOVresultR0;R1=24. No numericconstant assumptionsuntilpooldecoded.\n\nUnsignedR1>=R0 skipcall. Otherwise R0=R0-R1mod2^32;BL absolute0x40 withR1threshold,liveR2/R3,S0conversionstate/S1onbranch. Targetoutsidelockedflash,externaldependencysemanticsunknown. POP R0,PC alwaysreturnsfullentryR7,overwritescalculatedvalue/externalreturn;8frame released. FloatoperationsmaymodifyFPSCR flags; preserveinstructionsemantics,no algebraiccollapse/externaltimingclaim. NoMMIO/C/freeze/fullcoverageclaim. Following12bytesF0..FCnotcode.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
