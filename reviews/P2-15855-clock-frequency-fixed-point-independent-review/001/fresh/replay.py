from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x4d38ea;end=0x4d3914
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
o=b/'reviews/P2-15855-clock-frequency-fixed-point-independent-review/001/fresh';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Clock frequency fixed-point calculation, 0x4D38EA..0x4D3914\n\nPartial; accepted:false.42 instruction bytes. Leaf no stack. input=entryR0, requested=entryR1, exponent=entryR2, output=entryR3. Ordered architectural operations:\n\nS0bits=requested\nS0=VCVT.F32.U32(S0bits)\nR1=1\nR2=LSL_register(1,exponent) // uses low8 of exponent, zero for shifts>=32\nR0=UDIV(input,R2)\nS1bits=R0\nS1=VCVT.F32.U32(S1bits)\nS0=VDIV.F32(S0,S1)\nS0bits=VCVT.U32.F32_fixed(S0,fractional_bits=15)\nword[output]=S0bits\nreturn0\n\nRetains single-precision rounding/conversion steps, not collapsed to integer ratio. Output pointer unchecked; R1=1,R2=shiftresult,R3=output,R4-R12/SP unchanged; S0/S1 changed. UDIV zero denominator depends on CCR.DIV_0_TRP; floating zero denominator/NaN/overflow/conversion and FP availability depend on architectural FP state. No universal normal result asserted for these boundaries; FP flags not discarded from behavioral scope. Numeric FP and fault behavior not independently executed yet. No C/admission/gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
