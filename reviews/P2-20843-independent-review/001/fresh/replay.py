from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47cd68;end=0x47cde2
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
o=b/'analysis/review-isolated-P2-20843/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Word divisor normalization and fifteen-bit quotient stage\n\nPartial/unaccepted;122instructionbytes. CD68 entryR3zero fromearlierpath,R2>=65536. UnsignedR2<01000000→pendingCE3A beforeframe. OtherwisePUSH R4..R7,LR20;R7=CLZ(R2),R4=CLZ(R1),R6=15-R7,R5=R7-R4;R3=ARM_LSR(R2,R6),LR=R7+17,R2=ARM_ROR(R2,R6),R5+=32,R2 XOR=R3;SUBS R7,R5,15;unsigned<=→CD04 earliermappedcontinuation,20frame maintained.\nCD92 alsoenteredfromearlierCCD2 normalizationwith20frame: R1 XOR=R0;R6=32-R4;R0=ARM_LSL(R0,R4);R1=ARM_ROR(R1,R6);R1 XOR=R0. IP=UDIV(R1,R3);R1-=R3*IP;UMULL R4low,R5high=R2*IP;SUBS R0,R0,R4;SBCS R1,R1,R5;ifborrow:IP--;ADDS R0,R0,R2;ADCS R1,R1,R3.\nCDB8 unsignedR7<15→pendingCDE2. OtherwiseR7-=15;R1=(R1<<15)|(R0logicalright17);R6=UDIV(R1,R3);R1-=R3*R6;UMULL R4low,R5high=R2*R6;RSBS R0,R4,R0LSL15 computes(oldR0<<15)-R4;SBCS R1,R1,R5;ifborrow:R6--;ADDS R0,R0,R2;ADCS R1,R1,R3. CDDE IP=R6|(IP<<15);fallthroughpendingCDE2.\nArithmeticmod32exceptUMULL64,ARMregistershiftlow8semantics,carry/borrowexact. Shared20frame stilllive. No arithmeticcompleteness/C/freezeclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
