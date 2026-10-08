from pathlib import Path
import struct,json,hashlib
D=Path(__file__).resolve().parent;root=D.parents[2]
def initialized_record(raw):
 word=lambda a:struct.unpack_from('<I',raw,a-0x438000)[0];record=0x75d3f4;src=record+word(record);end=src+(word(record+4)>>1);out=bytearray();p=src
 while p!=end:
  token=raw[p-0x438000];p+=1;literals=token&3;match=token>>4
  if not literals:literals=raw[p-0x438000]+3;p+=1
  if match==15:match=raw[p-0x438000]+15;p+=1
  for i in range(literals-1):out.append(raw[p-0x438000]);p+=1
  if match:
   offset=raw[p-0x438000];p+=1;high=(token>>2)&3
   if high==3:high=raw[p-0x438000];p+=1
   offset+=high<<8;assert 0<offset<=len(out)
   for i in range(match+2):out.append(out[-offset])
 assert len(out)==0x4558
 expected=json.loads((root/'g2/analysis/audio-dispatch-initializer-closure-2026-10-08/results.json').read_text())['decoded_sha256'];assert hashlib.sha256(out).hexdigest()==expected
 return out
if __name__=='__main__':
 blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';out=initialized_record(blob[32:]);table=list(struct.unpack_from('<27I',out,0x2a8));(D/'startup-evidence.json').write_text(json.dumps(dict(initialized_record='0x75d3f4',decoded_sha256=hashlib.sha256(out).hexdigest(),initial_revision=hex(struct.unpack_from('<I',out,0x1e8)[0]),transition_table_address='0x200002a8',transition_table=[dict(index=i,thumb_pointer=hex(v),instruction_entry=hex(v&~1)) for i,v in enumerate(table)],method='Decode authenticated record; reuse sealed original/C/Python record agreement. No runtime mutation proof.'),indent=2)+'\n');print('Authenticated startup revision and27 transition pointers decoded')
