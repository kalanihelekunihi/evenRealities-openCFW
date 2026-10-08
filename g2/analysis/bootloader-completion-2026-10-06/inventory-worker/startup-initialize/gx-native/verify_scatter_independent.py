"""Independent bounded file decoder: initializer data/address provenance only."""
from pathlib import Path
import hashlib,struct,json
ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
image=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert sha(image)=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
record=struct.unpack_from('<III',image,0x433104-0x410000)
assert 0x433104+record[0]==0x4341c0 and record[1]==1250 and record[2]==0x20000000
stream=image[0x241c0:0x241c0+625]
def decode(data):
 cursor=0;output=bytearray()
 def byte():
  nonlocal cursor
  assert cursor<len(data),'truncated stream'
  v=data[cursor];cursor+=1;return v
 while cursor<len(data):
  control=byte();literal=control&3;run=control>>4
  if literal==0:literal=byte()+3
  if run==15:run=byte()+15
  for _ in range(literal-1):output.append(byte())
  if run:
   low=byte();high=(control>>2)&3
   if high==3:high=byte()
   distance=low+256*high;assert 0<distance<=len(output),'invalid backreference'
   for _ in range(run+2):output.append(output[-distance])
  assert len(output)<=1371,'excess output'
 assert cursor==len(data)
 return bytes(output)
output=decode(stream);assert len(output)==1371
original=json.loads((HERE/'scatter-selector-table.json').read_text())
assert sha(output)==original['output_sha256']=='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
table=output[0x158:0x158+108];assert sha(table)==original['callback_table_sha256']
targets=struct.unpack('<27I',table)
assert [hex(x) for x in targets]==[r['thumb_target'] for r in original['selectors']]
assert all(0x410000<=x<0x434000 and x&1 for x in targets)
assert all(image[(x&~1)-0x410000:(x&~1)-0x410000+2]==bytes.fromhex('7047') for x in targets[24:])
# Hold-out against prior whole-startup receipt constant, not invented current metadata.
reference=ROOT/'g2/components/bootloader/main_init/verify_startup_integrated.py'
assert original['output_sha256'] in reference.read_text()
controls=[]
for name,bad in [('truncated',stream[:-1]),('byte_mutation',stream[:20]+bytes([stream[20]^1])+stream[21:])]:
 try:modified=decode(bad);rejected=sha(modified)!=sha(output)
 except AssertionError:rejected=True
 assert rejected;controls.append(dict(name=name,rejected=True))
result=dict(status='PASS',method='Independent bounded Python file decoder versus original-instruction/native-C receipt and pre-existing whole-startup digest',original_sha256=sha(image),stream_sha256=sha(stream),output_sha256=sha(output),callback_table_sha256=sha(table),targets=[hex(x) for x in targets],record_raw=image[0x23104:0x23110].hex(),negative_controls=controls,reference_sha256=sha(reference.read_bytes()),limits=['Independent implementation and receipt/held-out digest agreement; not an independent physical acquisition of firmware.','Stored callback addresses are data provenance, not implemented target bodies or complete compressed-stream source reconstruction.'])
(HERE/'scatter-independent-provenance.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS independent1371bytes/27targets/2negativecontrols')
