from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x514070;end=0x5140c6
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
o=b/'/private/tmp/independent-ring-map-3';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Backing descriptor construction, 0x514070..0x5140C6,86 bytes\nPUSH entryR0,R1,R2,R3,R4,R5,R6,LR32\nR5=entryR0 destination; R4=entryR1 selector; R6=entryR2 requestedbytes\nR0=0; R0=R4; call514050()\nR1=byte[R0+24]\nif R1!=0:\n R6=u32(R6+31)&FFFFFFE0; R2=32; R1=R6; call4841D8()\nelse:\n if R4 in {0,1,2}: R2=8; R1=R6; call4841D8()\n else: R1=R6; call484180()\nword[SP+8]=R0; word[SP+12]=R0; word[SP]=R6; word[SP+4]=R4\nR0=R5; R1=SP; R2=16; call439C04()\nPOP R0,R1,R2,R3,R4,R5,R6,PC; SP+=32; return\n\nAllocatorR0still514050returnedcontextuntilchild, noselectorcontextreplacement. Localdescriptor[size,selector,allocatedptr,allocatedptr] copied16bytes toentrydestination. FinalPOPnormallyR0actualsize/R1selector/R2ptr/R3ptr, notcopyresult; alias/childwritescanaltertheseactualstackslots. 32bytealignmentwrapcanproduce0, noallocationNULLvalidation beforedescriptorcopy. Alignment8forselectors0/1/2whencontextbyte24zero. Ownership/lifetime unresolved.\n\nPartial; accepted:false. Ordered instructions, wrap32 and signedconditions retained; childcontracts, architecturalfault/alias/concurrentstate/lifetime conditional. No C, admission, freeze, gate or physicalqualification.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
