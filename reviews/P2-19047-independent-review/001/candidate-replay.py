from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x468b36;end=0x468bb6
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-payload-zero-byte-global-pair-snapshot-flag-and-stack15-builder-19448-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Payloadzerobyte468B36..468BB6\n\nPartial,unaccepted;128instructionbytes.Inherited32frame,R4savedpayloadbyte0. Fresh43D0CEbit1setR0literal468C24;freshbyte[R0+1]toR1toSP12,THENfreshbyte[R0]toR0toSP8;SP4literal4690F8,SP0=425,R3literal4690D8,R2literal4690DC,R1literal4690E0,R0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 FIRSTR1literal4690FC THENR0literal468C24;freshbyte[R0+1]toR2toSP0,THENfreshbyte[R0]toR3;R2R1,R0=0x0C800000 to43CE9E.\n\nR1literal469100(destination),R0literal468C24(source);freshsourcebyte0toR2 thenstoredestbyte0;freshsourcebyte1toR0 thenstoredestbyte1;R0=1 storedestbyte2. Reads/storesinterleaved,notassumedatomicpaircopy. R0=15storebyteSP16;R0=5storewordSP0(extraargument);R3=0,R2=1,R1SP16,R0=16 to465480. Branch468BB4->468C20. No builderresulttest orchildownershipcontractininterval. Exactreplay only,no gates/runtime/acceptance.Nextnonzerobytearmexcluded.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
