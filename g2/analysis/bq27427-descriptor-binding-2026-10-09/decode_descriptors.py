from pathlib import Path
import struct,json,hashlib
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];word=lambda a:struct.unpack_from('<I',raw,a-0x438000)[0];record=0x75d3f4;src=record+word(record);encoded=word(record+4);dest=word(record+8);end=src+(encoded>>1);assert encoded&1==0 and dest==0x20000000
out=bytearray();p=src;tokens=0
while p!=end:
 assert p<end
 token=raw[p-0x438000];p+=1;literals=token&3;match=token>>4
 if not literals:literals=raw[p-0x438000]+3;p+=1
 if match==15:match=raw[p-0x438000]+15;p+=1
 for i in range(literals-1):out.append(raw[p-0x438000]);p+=1
 if match:
  offset=raw[p-0x438000];p+=1;high=(token>>2)&3
  if high==3:high=raw[p-0x438000];p+=1
  offset+=high<<8;assert 0<offset<=len(out)
  for i in range(match+2):out.append(out[-offset])
 tokens+=1
assert len(out)==0x4558

start=0x6ec;table=bytes(out[start:start+56]);rows=[]
for i in range(7):
 b=table[8*i:8*i+8]
 rows.append(dict(index=i,ram_address=hex(dest+start+8*i),bytes=b.hex(),subclass=b[0],absolute_offset=b[1],block=b[1]>>5,offset_in_block=b[1]&31,type_byte=b[2],tail=b[3:].hex()))
(D/'descriptor-results.json').write_text(json.dumps(dict(firmware_sha256=hashlib.sha256(blob).hexdigest(),raw_sha256=hashlib.sha256(raw).hexdigest(),record=hex(record),source=hex(src),source_end=hex(end),compressed_bytes=encoded>>1,destination=hex(dest),decoded_bytes=len(out),decoded_sha256=hashlib.sha256(out).hexdigest(),table_ram='0x200006ec',table_sha256=hashlib.sha256(table).hexdigest(),rows=rows),indent=2)+'\n')
print(json.dumps(rows,indent=2))
