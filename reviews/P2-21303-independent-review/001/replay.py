from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x482ef6;end=0x482f72
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
o=b/'analysis/review-isolated-P2-21303/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Two-alpha composition thresholds and normalized blend\n\nPartial/unaccepted;124 instructionbytes482EF6..482F72. PUSH{R0,R4,LR}12bytes,SUBSP4,total16. FirstwordSP4..7 savedentryR0;SP0 initiallyunwritten. FreshfirstalphaSP7>=253returnsfreshfirstwordSP4withoutinitializingSP0. OtherwisestoreentryR1secondwordSP0;freshsecondalphaSP3<3returnsfirstword. ThenfreshfirstalphaSP7<3returnssecondwordSP0. Bothalphasintermediate: freshsecondalphaSP3==255 loadsR1=SP0,R0=SP4,call482E4C liveR2/R3;storehelperresultSP0,reloadR0,return.\n\nOtherpathfreshfirstalphaSP7→R0,R0=255-R0;freshsecondalphaSP3→R4,R4=255-R4;R4*=R0mod,ASR8,R4=255-R4mod (compositealpha). FreshfirstalphaSP7→R1,R1*=255mod;R0=UXTB(R4),UDIV R0=R1/R0 unsigned;storelowbyteR0 SP7,modifyingfirstalpha. ReloadsecondwordSP0→R1,modifiedfirstwordSP4→R0,call482E4C liveR2/R3;storehelperresultSP0 thenlowbytecurrentR4→SP3;reloadwordSP0→R0. AllpathsPOP{R1,R2,R4,PC}16bytes:R1=SP0 possiblyunwrittenfirstshortcut,R2=savedfirstwordpossiblyalphamodified,R4restored. PreserveexactASR/UDIV/truncations,thresholdorderandreturnaliases;noassumedfloatingformula. Following482F72..74zeroexcluded. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
