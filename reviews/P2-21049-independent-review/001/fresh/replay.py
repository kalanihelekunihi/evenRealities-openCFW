from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47f56e;end=0x47f5f6
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
o=b/'analysis/review-isolated-P2-21049/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Conditional three-helper return and indexed record-query prefix\n\nPartial/unaccepted;136instructionbytes47F56E..47F5F6. F56E PUSH R4,LR8;R4literalFFBCvalue;4807FC(100,R4,256,256). Fullzero returnszero. Nonzero→4807FC(100,literalFFC0value,1,1). Fullnonzero returnssecondresultunchanged. Secondzero→independentlyfreshword throughliteral4800F4 OR1stored, then4807FC(100,R4,256,256),returnsfullthirdresult. POP R4,PC releases8; no normalization or earlyfallbackinvented.\n\nF5B8 PUSH R3,R4,R5,LR16;SUBSP24,40totalframe;R4fullentryR0. EF18(SP+4,LOW8(entryR0),liveR2/R3),fullnonzerobranchesF6EEoutsideprefixwithframeactive. Zero→freshSP4pointer dereferencedword, freshSP8mask; anyintersectionnonzero setsR0=0 thenbranchesF6EE. Otherwise LOW8(entryR0)==23 only, independentlyfreshwordthroughFAE0bit27zero setsR0=1 thenbranchesF6EE; bit27nonzero orotherindexcontinuesF5F6withframeactive,R4entryindex andlocal16byterecordatSP4fromEF18. No localrecordinitializationassumptionbeyondhelper call; no prefixreturn/unwind claim. Externalhelper/pointedownershipunresolved; noMMIO/C/freeze/fullcoverageclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
