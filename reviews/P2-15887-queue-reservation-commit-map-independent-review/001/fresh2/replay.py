from pathlib import Path
import json,hashlib,re,subprocess,tempfile
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';start=0x538fb4;end=0x53901a
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
o=Path('reviews/P2-15887-queue-reservation-commit-map-independent-review/001/fresh2');o.mkdir(parents=True,exist_ok=False);(o/'instructions.json').write_text(json.dumps([dict(start=start,end=end,instructions=rows)],indent=2)+'\n');(o/'disassembly.txt').write_text(rawtext);refs=sorted(set(int(m[1],16) for row in rows if (m:=re.search(r'@\s*\(?([0-9a-f]{6,8})',row['operands'])) and 'pc' in row['operands']))
(o/'references.json').write_text(json.dumps([dict(address=a,bytes=d[a-0x438000:a-0x438000+4].hex(),value=int.from_bytes(d[a-0x438000:a-0x438000+4],'little')) for a in refs],indent=2)+'\n')
(o/'pseudocode.md').write_text('# Queue reservation commit, 0x538FB4..0x53901A\n\nPartial; accepted:false.102 original instruction bytes,leafnoframe/children. CachequeueR2entryR0;entryR1markerflag. NULL/badmasked01FFFFFFsignature!=01CDCDCDreturns2;word[q16]==word[q20]returns7. Validpendingpathordered:\n\nnode=freshword[q20]\nmarker=(u8(flag)!=0 ?1:0)|word[word[q36]+8] // indexaddress itself,not pointee\nword[node]=marker\nword[node+4]=freshword[q32]\nword[q20]=u32(node+8)\nword[q16]=freshword[q20]\nif word[q8]>=20080000:DMB SY\nvalue=freshbyte[q32] // not full producerword\npublish_pointer=word[freshword[q36]+12]\nword[publish_pointer]=value\nreturn0\n\nR2queue retained. Queueproducer32notincrementedhere;allocationalreadydidso. Markerappendedafterreserveddata, consumes8bytes. Pointerpublicationlast afterconditionalbarrier; fields/signature validatedonlyatentry. Outputaliases ormappingmutationcanalterfreshreads. Noenabledstatecheck,interruptmaskingorchainvalidation. PhysicalDMAvisibility,alignmentfaults/concurrencyunqualified. No C/admission/gates.\n')
(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(accepted=False,status='partial',input_sha256=h(d),instruction_bytes=end-start,files={p.name:h(p.read_bytes()) for p in o.iterdir()}),indent=2)+'\n');print('PASS',end-start)
