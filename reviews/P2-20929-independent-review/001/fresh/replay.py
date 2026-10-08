from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47dd08;end=0x47dd62
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
o=b/'analysis/review-isolated-P2-20929/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Three decimal-result slots packed without field masks\n\nPartial/unaccepted;90instructionbytes47DD08..47DD62. PUSH R0,R1,R2,R3,R4,LR24. SP0=literal47E288 initialpointer;43C0E4(SP+4,12,0,liveR3);R4=0. Loop reads pointer fromSP0 then freshunsignedbyte: zero exits. SignedR4>=3 exits. Otherwise independently reloadpointer andfreshbyte, wrapping subtract48 and unsignedcompare<10. Nondigit advances freshlyloadedSP0pointer by1 modulo2^32 andstoresit,thenrepeats. Digit calls48D874(freshSP0pointer,SP,10,liveR3); helper can update SP0 throughR1. FullreturnedR0 storedSP+4+4*R4, thenR4increments; repeats. Do not assume pointeradvancement or parser semantics beyond callcontract; digit path has no explicit caller pointerincrement.\nExit reads slot1SP4 intoR1,slot2SP8 intoR0,shiftsR0left8 modulo2^32, ORs slot1<<16 modulo2^32, reads slot3SP12 intoR1 andORs wholeunmaskedslot3. R0=(slot1<<16)|(slot2<<8)|slot3 modulo2^32; no low8fieldmasks,overflowvalidationor digitcountvalidation. Helper43C0E4 unresolved so unfilledslotvalues notassumedzero. SP+=16 discardsfourlocalwords;POP R4,PC restoresentryR4. R1finalslot3;R2/R3helperclobbers. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
