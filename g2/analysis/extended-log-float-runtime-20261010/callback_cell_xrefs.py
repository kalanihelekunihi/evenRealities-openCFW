"""Direct literal xrefs for the stock assert callback cell."""
import hashlib,json,re
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
base=0x438000;needle=(0x2007456c).to_bytes(4,'little')
locations=[];offset=0
while True:
    index=raw.find(needle,offset)
    if index<0:break
    locations.append(base+index);offset=index+1
assert locations==[0x43daa0,0x44b714,0x45fa88,0x53af50,0x569af4]
lines=(ROOT/'g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt').read_text().splitlines()
xrefs=[]
for i,line in enumerate(lines[:-1]):
    if any('0x'+format(a,'x') in line for a in locations):
        next_line=lines[i+1]
        assert re.search(r'ldr\s+r0, \[r3, #0\]',next_line),(line,next_line)
        xrefs.append({'literal_load':line.strip(),'cell_read':next_line.strip()})
assert len(xrefs)==17
receipt={'status':'PASS','cell':'0x2007456c','flash_literals':[hex(a) for a in locations],
         'direct_literal_xrefs':len(xrefs),'xrefs':xrefs,
         'limit':'Only direct PC-literal references. Computed writes, startup data copy and production callback target are not excluded by this scan.'}
(HERE/'callback_cell_xrefs.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','flash_literals':len(locations),'direct_read_xrefs':len(xrefs)}))
