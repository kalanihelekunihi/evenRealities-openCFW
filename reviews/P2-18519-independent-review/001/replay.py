from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x460b12;end=0x460b68
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
o=b/'analysis/apollo-main-diagnostic-fixed-library-pre-body-mask-gated-lookups-stride-reset-and-local-diagnostic-18920-map/001';o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Pre-body diagnostic460B12..460B68\nPartial;unaccepted.86 instructionbytes,inherits64frame/locals36,R5sourcebase,R6destbase,R7index. Entryonlybit1setfrom460B0A. R8=52 RESETSdeststride;R0=wrap32(R6+low32(R8*R7)+4);460084 liveargs. R1=fullresult,R0=SEPARATEcomputedfieldptr;45FFFE liveR2/R3. R1=wrap32(R6+low32(R8*R7));R1=freshbyte[R1+40]→SP16. R8=low32(R8*R7) REPLACESresetstridewithoffset;R1=wrap32(R6+R8),R1=freshword[R1+48]→SP12. SP8=fullselectorR0;R0=wordliteral46155C→SP4,R0=429→SP0,R3=wordliteral4611B8,R2=wordliteral4611BC,R1=wordliteral4611C0,R0=3;43D574. Localwritesnot savedslots;freshfieldreadsafterlookupcalls preserved. R8offsetatend,nextsharedjoin460B68excluded;bit1clearbypassdidnotperformreset52here. R9unchanged. Lookupwrappersdecodedbut46CACCchildcontractunresolved. Remainingmask/bodyselectionoutside span.\nNo C,gate/source admission,whole coverage or simulator/hardware proof.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
