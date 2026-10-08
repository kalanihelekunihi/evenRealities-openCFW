from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47e178;end=0x47e1ec
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
o=b/'analysis/review-isolated-P2-20953/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Flag-gated exact-count output with wrapping size rollover\n\nPartial/unaccepted;116instructionbytes47E178..47E1EC. PUSH R3,R4,R5,R6,R7,LR24;R4=entryR0,R5=entryR1. Freshbyte[pointerliteralE2B4]zero→R0=FFFFFFFE(-2)exit. OtherwiseR6=literalE2B8pointer;freshwordzero skipscapacityguard. Nonzero→freshword[pointerE2BC]+R5 modulo2^32;unsignedsum>=32769→47E06A(liveargs),thenword[R6]=0. Overflowwrapnotseparatelyrejected.\nR7=literalE2C0handlepointer;freshwordnonzero→output. Freshzero→freshword[R6]zero calls47E0C8(liveargs),else47E144(liveargs);fullreturnnonzero exitsunchangedR0(-5bylocalcontracts). Fullzero→output.\nOutputfreshword[R7]→R3;474682(entryR0,1,entryR1,R3). Fullresult!=R5→47E06A(liveargs),R0=FFFFFFFB(-5)exit. Equality→freshword[pointerE2BC]+R5modulo2^32 storedsameword;R0=0. ZeroentryR1canpass exactcountzero. Globalsreadatdistincttimes,nocachedhandle. POP R1,R4,R5,R6,R7,PC24 returnsR1=savedentryR3 subjecttohelperstackwrites;restorepreservedregs. No C/freeze/completenessclaim;externalhelpersemanticsremainunresolved.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
