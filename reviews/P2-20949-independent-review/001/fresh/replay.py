from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47e0c8;end=0x47e13e
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
o=b/'analysis/review-isolated-P2-20949/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Global handle assignment and exact thirty-two-byte local output\n\nPartial/unaccepted;118instructionbytes47E0C8..47E13E. PUSH R3,R4,R5,LR16;SP-=96,total112.47E090(liveargs);fullnonzero exitsunchangedR0. OtherwiseR0=literal47E2A8pointer;firstfreshword→R4;secondindependentfreshwordincrementmodulo2^32store.47DF28(liveargs);fullnonzero exitsunchangedR0. Otherwise47DE0A(SP+32,64,R4,liveR3);returnignored. R5=literal47E2C0handlepointer;474550(SP+32,address47E174,liveR2,R3);storefullresultglobalword,thenfreshreloadglobalwordforzerotest. Freshzero→-5exit (noadditionalcleanup). Nonzero→R2=freshword[pointerliteral47E2A4];48ED00(SP,R4,R2,liveR3),resultignored. Freshglobalhandle→R3;474682(SP,1,32,R3). Fullresult!=32→47E06A(liveargs) closesfreshglobalhandleandclearsit per recoveredcontract,thenR0=-5. Fullresult==32→storeR4 toword[pointerE2B8];store32 toword[pointerE2BC];R0=0. Successfulhandleleftassigned. SP+=100discards96localsandsavedentryR3;POP R4,R5,PC12. SP0..31localrecord,SP32..95formatbuffer;uninitializedbytesdependexternalhelpers. Do notcacheglobalhandleorcounteracrossfreshreads. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
