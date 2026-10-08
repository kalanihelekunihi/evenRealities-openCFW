from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x483de0;end=0x483e98
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
o=b/'analysis/review-isolated-P2-21375/fresh';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Unsigned handoff and fixed/general floating handlers\n\nPartial/unaccepted;184 instructionbytes483DE0..483E98 continuing88-byteframe483960. SharedunsignedvalueR0: orderedflagsR8SP20,widthR7SP16,precisionR4SP12,radixR10SP8,sign0SP4,valueR0SP0;reloadR3SP44,R2R6,R1SP40,R0R5;call48320A,R6=result. Common483E00 freshcursorSP48incrementstore,branch48398E.\n\nFixedentry483E08 freshcursorbyteF70→R8|=32,otherwiseunchanged. AlignedvarargaddressR0=(R9+7)&~7wrap,full8Bload d0[R0],R9=R0+8. OrderedflagsR8SP8,widthR7SP4,precisionR4SP0;reloadR3SP44,R2R6,R1SP40,R0R5;call483350,R6=result;freshcursorincrementstore,branch48398E.\n\nGeneral/scientificentry483E42 freshcursorbyteg103 or independentlyfreshG71→R8|=2048. FreshbyteE69 or independentlyfreshG71→R8|=32. Samealigned8Bvarargload/advance andstackflags,width,precision;reloadcallbackargs,call48364C;R6=result;freshcursorincrementstore,branch48398E. Exact rereads,stackorder andhelperselection retained. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
