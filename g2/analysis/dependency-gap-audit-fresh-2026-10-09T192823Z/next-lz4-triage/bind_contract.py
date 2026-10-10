from pathlib import Path
import json,hashlib,re
O=Path(__file__).resolve().parent;D=Path('g2/analysis/apollo-lz4-source-discriminator-20261009T211300Z');raw=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];base=0x438000;sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
for r in json.loads((D/'stock-bindings.json').read_text())['functions']+json.loads((D/'helper-bindings.json').read_text()):
 a,z=int(r['start'],16),int(r['end'],16);ck('range '+r['start'],sha(raw[a-base:z-base])==r['sha256'])
for f in ['original-disassembly.txt','helper-disassembly.txt']:
 valid=True
 for a,h in re.findall(r'^([0-9a-f]{8}): ([0-9a-f]+) ',(D/f).read_text(),re.M):
  a=int(a,16);v=bytes.fromhex(h);valid &= raw[a-base:a-base+len(v)]==v
 ck('all listing bytes '+f,valid)
def target(a):
 x=raw[a-base:a-base+4]
 if len(x)!=4:return None
 h1,h2=int.from_bytes(x[:2],'little'),int.from_bytes(x[2:],'little')
 if h1&0xf800!=0xf000 or h2&0xd000!=0xd000:return None
 s=(h1>>10)&1;i1=1^((h2>>13)&1)^s;i2=1^((h2>>11)&1)^s;imm=(s<<24)|(i1<<23)|(i2<<22)|((h1&1023)<<12)|((h2&2047)<<1)
 return a+4+(imm-(1<<25) if s else imm)
calls=[]
for a in range(base,base+len(raw)-3,2):
 t=target(a)
 if t in [0x54ee90,0x54ef08,0x54f338]:
  calls.append({'address':hex(a),'target':hex(t),'context_start':hex(a-24),'context_hex':raw[a-base-24:a-base+20].hex()})
ck('safe wrapper branch',target(0x54f34e)==0x54ef08)
# This detects encodings, not code/data classification or execution reachability.
r={'checks':checks,'all_pass':all(x['pass'] for x in checks),'direct_BL_encoding_candidates':calls,'listing_sha256':{f:sha((D/f).read_bytes()) for f in ['original-disassembly.txt','helper-disassembly.txt']},'scope':'Static raw Thumb BL encoding scan. Candidate callsites require containing-function classification; not every matched encoding is executable.'};(O/'CALLER-CONTRACT-BASELINE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
