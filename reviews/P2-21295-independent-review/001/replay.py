from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x482d88;end=0x482dd8
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
o=b/'analysis/review-isolated-P2-21295/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Empty-endpoint predicate, clear wrapper and computed link writes\n\nPartial/unaccepted;80 instructionbytes482D88..482DD8. Frameless482D88 nullR0descriptorreturns1withoutreads;otherwisefreshword[R0+4]→R1,nonnullreturns0withoutsecondfieldread. Zero firstfieldfreshword[R0+8]→R0;zero returns1,nonnull0;BXLR. Separate482DA4 PUSH{R7,LR}8bytes,R1=0,call482C9A withentryR0/liveR2/R3;POP{R0,PC}returns savedentryR7 overridingtraversalresult.\n\n482DAE PUSH{R2}4bytes first,beforetestingfullR1node. Nullnode skipall descriptorreads/writes,ADDSP4,BXLR,retainR0/R1. Nonnull freshword[entryR0descriptor]→R0,R0+=entryR1mod2^32,R1=SP,freshword[SP]→R1savedentryR2,storefullR1[R0];ADDSP4,BXLR. 482DC2 samebutR0+=4mod afterdescriptoroffset+node. BothhelpersR2retained,nonnullreturns computedstoreaddressR0 andsavedvalueR1;no descriptor/null/offsetguard. Stackfreshread participatesalias-sensitiveordering. Thesewritesresolve nodehelpermemoryeffects atnode+descriptorword andnode+descriptorword+4; do notassumefixedoffset. No C,freeze,wholecoverage or equalityclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
