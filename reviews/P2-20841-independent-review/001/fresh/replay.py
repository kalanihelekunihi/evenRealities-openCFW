from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x47ccd2;end=0x47cd68
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
o=b/'analysis/review-isolated-P2-20841/fresh';o.mkdir(parents=True,exist_ok=True);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Two-word nonzero high divisor normalization and correction\n\nPartial/unaccepted;150 instruction bytes. CCD2 CMP R0,R2 thenSBCS IP,R1,R3;carryzero→CCC8 zeroquotient/originalremainder. ElseunsignedR3>=65536→CD40.\nLowhighwordpath:PUSH R4..R7,LR20;R7=CLZ(R3),R4=CLZ(R1),LR=R7-15,R5=R7-R4;R3 XOR=R2;R6=32-LR;R2=ARM_LSL(R2,LR);R3=ARM_ROR(R3,R6);R3 XOR=R2. SUBS R7,R5,15;unsignedHI→pendingCD92 (20frame remains).\nOtherwiseR4-=15;R4+=R5;R1 XOR=R0;R6=32-R4;R0=ARM_LSL(R0,R4);R1=ARM_ROR(R1,R6);R1 XOR=R0. R6=UDIV(R1,R3);R1-=R3*R6;UMULL R4low,R5high=R2*R6. SUBS R0,R0,R4;SBCS R1,R1,R5;carryone→CD2C;elseR6--;ADDS R0,R0,R2;ADCS R1,R1,R3.\nCD2C:R2=R0 XOR R1;R3=ARM_LSR(R1,LR);R2=ARM_ROR(R2,LR);R1=0;R2 XOR=R3;R0=R6;POP R4..R7,PC20. Use ARM register-shift semantics including low8 count; no host maskedshift substitution.\nCD40:PUSH R4,R5 8;IP=UDIV(R1,R3);R1-=R3*IP;UMULL R4low,R5high=R2*IP;SUBS R0,R0,R4;SBCS R1,R1,R5;carryone→CD5C;elseIP--;ADDS R0,R0,R2;ADCS R1,R1,R3. CD5C POP R4,R5;R2=R0,R3=R1,R0=IP,R1=0;BXLR.\nAll arithmeticmod32 exceptUMULL64;borrow/carry retainedexactly. PendingCD92 continuation andCD68 entry remain. No C/freeze/completenessclaim.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
