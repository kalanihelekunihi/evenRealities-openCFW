from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x46949a;end=0x46951a
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-handler4-null-length-guards-and-three-byte-diagnostics-19502-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Handler entry 0x46949A..0x46951A\n\nPartial/unaccepted;128 instruction bytes. PUSH R4/R5/LR thenSUBSP20 creates32-byteframe. FULL R0!=4 orFULL R1==0 orFULL R2==0 eachbranches469550 outsidechunk. Otherwise unsignedbyte[R1] ->R4; call46919E withliveoriginalargs, R5=FULLboolresult.\n\nFresh43D0CE bit1 enablesdiagnostic: loadunsignedbyte[address literal469B54] fresh andstoreSP16; temporaryR0low8R4 ->SP12; temporaryR0low8R5 ->SP8, preservingR4/R5. SP4=literal469B7C,SP0=189,R3=literal469B80,R2=literal469B38,R1=literal469B3C,R0=4 ->43D574.\n\nSeparatefresh43D0CE bit0 orconditional thirdfreshbit2 enables secondarydiagnostic. R1=literal469B84; independentlyloadunsignedbyte[address literal469B54] again ->SP4; temporarylow8R4 ->SP0; R3=low8R5 viaR3temporary;R2=R1;R0=0x10C00000 ->43CE9E. Do not mergetwo globalreads ortruncateR4/R5inplace. SP0/4/8/12/16 arelocaldiagnostics; savedregisters atSP20/24/28 remainintact. R4payloadbyte/R5boolliveat46951A. Childcontracts unresolved; no C,freezeorwholefunctionclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
