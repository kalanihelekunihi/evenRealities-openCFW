from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x483c60;end=0x483ce0
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
o=b/'analysis/review-isolated-P2-21369/fresh';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Wide integer handoff and signed long/byte/halfword paths\n\nPartial/unaccepted;128 instructionbytes483C60..483CE0,continuation88-byteframe483960. WidepathUXTB R12sign→SP8;R2/R3magnitude→SP0/4;SP12 gap unwritten in this path. ReloadR3SP44entry2,R2R6position,R1SP40entry1,R0R5callback;48329C;R6=result,branch483E00unresolved. Previous flags/width/precision/radixpairSP32/28/24/16/20 retained.\n\n483C7Cflagsbit8clear→483CBC. Set loadword[R9]R0,R9+=4;signR1=1ifsignedR0negativeelse0; signedR0<1negateswrapping,elsekeeps. Ordered flagsSP20,widthSP16,precisionSP12,radixR10SP8,UXTBsignSP4,magnitudeSP0. ReloadcallbackargsR3SP44,R2R6,R1SP40,R0R5;call48320A,R6=result,branch483E00.\n\n483CBCbit6set loadfullwordvararg,nextR9+=4,UXTB R0 (unsigned byte even within signed conversion),branch483CE8 unresolved. Elsebit7set loadfullword,nextR9+=4,SXTH R0,branch483CE8. Bit7clear→483CE0unresolved. Preserve precedencebit6beforebit7 and byte zero extension exactly. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
