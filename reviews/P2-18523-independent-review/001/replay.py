from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x460bd0;end=0x460c3a
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-record-lookup-five-output-arguments-and-failure-diagnostic-prefix-18924-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text("# Record lookup460BD0..460C3A\nPartial;unaccepted.106 instructionbytes,inherits64frame/locals36,R4headerbyte1,R5sourcebase,R6destbase,R7index,R9sourcestride44. Enterzerosourceword8. R8=52 RESETSdeststride. OrderedR0=wrap32(R6+low32(R8*R7)+40)→SP0 callerfifthargument;R3=wrap32(R6+low32(R8*R7)+36);R2=wrap32(R6+low32(R8*R7)+4);R1=wrap32(R6+low32(R8*R7));R0=wrap32(R5+low32(R9*R7));R0=freshword[R0+48];460450 decoded8-recordlookup withfiveoutputarguments. Fullzeroresult→460A44 alreadymappedalternativekeyupdate;nonnull→fresh43D0CE bit1clear→460C3Aexternaljoin. SetR0=FRESHcomputedsourceword48→SP8;R0=wordliteral461564→SP4,R0=433→SP0(overwritesfifthargAFTERlookup),R3=wordliteral4611B8,R2=wordliteral4611BC,R1=wordliteral4611C0,R0=1;43D574. R9stride44retainedthroughchild,thecalledroutine'sR9restoredbycallee. Freshsourcewordreadafterchildmayobserveeffects. No cachedkeyreuse/no secondlookuphere. LocalSP0/4/8not savedregs;remainingdiagnostic/negativeexitoutside span.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n")
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
