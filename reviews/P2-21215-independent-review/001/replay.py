from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x481d7a;end=0x481de8
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-format-raw-exponent-fraction-special-three-byte-copy-21614-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Raw exponent/fraction checks and special three-byte copy\n\nPartial/unaccepted;110 instruction bytes481D7A..481DE8. Continues481836232frame;rawlowL/highHwordSP8/12,R11conversion,R12prefix-endpointer. ReloadL/H;T=(H<<1mod2^32)|(L>>31);R6=ASR(T,21),R7=ASR(T,31). IfR7==FFFFFFFF ANDR6==FFFFFFFF,formU=(H<<12mod2^32)|(L>>20),V=L<<12mod2^32;nonzero(U|V)→firstspecialpath. PreserveIT EQcompareandexactshiftpredicates. Firstspecial:R5=conversion-97mod2^32;SP32=3;ifunsignedR5<26 sourceADR4826E8 at481DE2;elseADR4826EC at481DB0.\n\nOtherpathreloadL/H;Q=ASR(H<<1mod2^32,21);ifQ!=-1 or(H<<12mod2^32)!=0→481DE8 unresolvednormalization. Else secondspecial:R5conversion-97;SP32=3;unsignedR5<26→481E14 unresolvedsourceADR;elseADR4826F4 at481DD4. Note secondpredicateonlychecksHfractionbits,notL; do notsubstitutestandardisinf/isnanwithoutprovingprecedingfirstpredicatehandling.\n\nCommon481DD8:R2=3,R0=R12destination,R1source;call439BE4 withliveR3;ignorefullreturn;branch4824AC. Specialstringbytes/helpersourcedataunresolved;copysemanticsrequirehelperrecovery. No C/freeze/fullcoverage/equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
