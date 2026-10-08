from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x481142;end=0x481230
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-indexed-mask-set-seven-word-two-bank-clear-middle-21568-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Indexed mask set and seven-word two-bank clear\n\nPartial/unaccepted;238 instruction bytes481142..481230. Continues4810B0,40-byteframe;R5indexedbankpointer,R6entrybankselector,R7inputpointer,SP0mask,SP8saved473940result. Mode1:freshword[R5] ORfreshwordSP0 thenstore;R6=UXTB(R6);if==2 R5+=112 thenanotherfreshword ORfreshSP0maskstore. Branch4812E8 unresolvedepilogue.\n\nMode2: testUXTBbankselector==1;true skipsfirstsevenupdates. Otherwise for k=0..6 inincreasingorder: freshword[R7+4*k] mask;loadliteralpointer slots481768+4*k;freshword[thatpointer] AND~mask;storeback. Theseareunrolledorderedupdates,notbulkcopy;eachinputreadprecedestargetread/write. ThenR6=UXTB(R6);if==0 skipsecondbank. Otherwise repeatsevenupdateswithfreshinputwords again andpointerliteral slots481784+4*k. Thusselector0firstbankonly,1secondbankonly,2..255bothbanks;no bankrangevalidation. Preserve input/targetaliasing andrereadsbetweenselectedbanks. No loopcounterorboundtestexists inencodedunrolledsequence. Branch4812E8 unresolvedrestore/return. No C/freeze/fullcoverage/equality claim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
