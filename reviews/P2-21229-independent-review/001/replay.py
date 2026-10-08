from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x482040;end=0x4820bc
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-decimal-float-leading-zero-trim-retained-digit-carry-rounding-21628-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text("# Decimal leading-zero trim, retained digit and carry scan\n\nPartial/unaccepted;124 instruction bytes482040..4820BC. Continues481836232frame,R6cursor,R8lowercaseconversion. R6=cursor-SP133mod2^32,R4=SP133. Whilefreshbyte[R4]==48:reloadSP0exponentdecrement1store;R6--;R4++;repeat. No encodedlength/boundcheckinleadingzero scan. Retainedcountbase: R8f102→wordSP0+1;elseR8e101→1;other→0. AddprecisionwordSP56mod2^32→R0. IfsignedR6<R0,R0=R6-1;negativeR0→4820BC. Note strictLTclamp differsfromordinarymin.\n\nIfsignedR0<R6,freshbyte[R4+R0]>52signed(ASCII'4')→R1=57('9');elseR1=48('0'). R0>=R6→R1=48. R2=R0,R3=R4-1,R5=R3+R2. Backwardscan:freshbyte[R5]postdecrement→R6;R2--;ifbyte==R1 R0--repeat. R1==57→freshbyte[R4+R2]increment1storelow8. IfsignedR2negative:reloadSP0exponent+1store,R4=R3(previousbase-1),R0++;elseunchanged. Joins4820BC. Preservetrim/scanunboundedencodedreads,sentineldependency,overflowandorderedwrites;no ties-to-even substitution,C/freeze/fullcoverage/equality claim.\n")
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
