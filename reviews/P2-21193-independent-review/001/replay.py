from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x481836;end=0x481884
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-callback-byte-output-format-loop-stack-initialization-prefix-21592-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Callback byte output format loop stack initialization prefix\n\nPartial/unaccepted;78 instruction bytes481836..481884. STMDB R0,R4,R5,R6,R7,R8,R9,R10,R11,LR40;SUBSP192 totals232frame. R10entryR2inputbytepointer;SP16entryR1callbackstate;R1=SP66,SP172=R1;R2wordSP232=fifthentryargument;R9entryR3;byteSP67=low8fifthargument. SavedentryR0callbackaddress atSP192. R0counter0;storeSP52 thenfreshbyte[R10]. NUL→481884 unresolvedend;byte37percent→initializewordsSP28,32,36,40,44,48to0(inthatorder),branch48188E unresolvedparser. Otherbyte→freshLDRB[R10]postincrement1→R1;R0currentwordSP16;R2callbackaddressSP192;BLXR2 withliveR3. Fullcallbackresult→SP16;zero→4824E4 unresolvedfailure;nonzero reloadcounterSP52 increment1mod2^32,repeat. Initialpeek andcallbackbyteareseparatefreshreads;callbackmaymodifyfutureinput/state. CallbackR0state,R1byte,R2callbackaddress,R3live;R9/R10 retainedunderABI. No finalreturn/unwindcovered,no C/freeze/fullcoverage/equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
