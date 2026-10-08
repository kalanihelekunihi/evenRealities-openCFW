from pathlib import Path
import struct,hashlib,json
D=Path(__file__).resolve().parent;root=D.parents[2]
def decode_itcm(raw):
 word=lambda a:struct.unpack_from('<I',raw,a-0x438000)[0];record=0x75d3e4;src=record+word(record);size=word(record+4)>>1;assert src==0x79430e and size==22 and word(record+8)==0x40;out=bytearray();p=src;end=src+size
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
 assert len(out)==24 and hashlib.sha256(out).hexdigest()=='0676154418085b0630f2a20cc50fbbe3967dd2d9b7794fe1aad3f6af14f2fb83'
 return bytes(out)
