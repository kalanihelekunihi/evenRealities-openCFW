from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x46951a;end=0x469576
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-handler4-byte-one-zero-transition-actions-and-zero-return-19504-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Handler tail 0x46951A..0x469576\n\nPartial/unaccepted;92 instruction bytes. Inherit32-byteframe,R4payloadbyte,R5fullcontextbool. TemporaryR0=low8R4; if!=1 branch469556. Then temporaryR0=low8R5; if!=0 branch469556. Matching1/0 setsR0=1,R1=literal469B88,storebyte1[R1],R0=1 ->49BF24 withliveotherargs. Fallthrough469538 calls45A568 withliveargs; FULLresult1 calls45A8EE(266,0,0,500); otherwise skips.469550explicitR0=0;469552ADDSP20,POP R4/R5/PC12 restores32-byteframe.\n\n469556 truncatesR4inplacelow8; ifnonzero branches469572. ZerotruncatesR5inplacelow8; FULLlowbyteR5!=1 branches469572. Matching0/1 setsR0=0,R1=literal469B88,storebyte0[R1];R0=0 ->4691BC withliveotherargs, thenbackwardbranch469538 sharedmodecheck. Othercombination469572explicitR0=0 ->469552epilogue. Allrecordedentryguards/actions therefore return0; retainchildsideeffects andeachorderedcall. Following469576zeroalignment andADR-targetdata469578/57C excluded. Childcontracts unresolved; no C,freezeorwholecorpusclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
