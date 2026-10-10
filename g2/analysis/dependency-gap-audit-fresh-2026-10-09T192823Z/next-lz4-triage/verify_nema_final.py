from pathlib import Path
import json,struct,re,hashlib
O=Path(__file__).resolve().parent;D=Path('g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track');ns={"__file__":str(O/"nema_target.py")};exec((O/'nema_target.py').read_text().split('raw=')[0],ns);body=ns['b'];ss=ns['ss'];sym=next(x for x in ns['sy'] if x['name']=='nema_cl_bind_sectored_circular');text=ss[sym['section']];off=sym['value']&~1;c=body[text[4]+off:text[4]+off+sym['size']];sha=lambda b:hashlib.sha256(b).hexdigest();raw=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];base=0x438000;a=0x5143d4;stock=raw[a-base:0x5144ba-base];checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
ck('locked extent hash',len(stock)==230 and sha(stock)=='1b72806af461fbd44dc0a8928e9a4b4493d124242f8f89f7d5820d0c8c692b6d')
ck('candidate symbol full hash',len(c)==222 and sha(c)=='e8b0d7c0bc4363c4f2d266fced1ff65764b59e4ec84346ffd8570f191616ddca')
for f,data,b in [('stock-sectored-disasm.txt',stock,a),('iar-sectored-disasm.txt',body[text[4]:text[4]+text[5]],0)]:
 ok=True;count=0
 for ad,hs in re.findall(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+){1,2})\t', (D/f).read_text(),re.M):
  ad=int(ad,16);v=b''.join(int(h,16).to_bytes(2,'little') for h in hs.split());ok &= data[ad-b:ad-b+len(v)]==v;count+=1
 ck('listing bytes '+f,ok and count>30)
ck('extra eight bytes exact',stock[162:170]==bytes.fromhex('826922f020028261'))
ck('last eight executable epilogue',stock[-8:]==bytes.fromhex('31684c6001b0f0bd'))
ck('candidate corresponding MOVS',c[162:166]==bytes.fromhex('00204860'))
ck('stock branch into extra update',stock[132:134]==bytes.fromhex('0ddb'))
# Independently re-encode both Thumb branches and PC12.
def encode(pc,target,link):
 d=(target-pc-4)&0x1ffffff;s=d>>24;j1=1^((d>>23)&1)^s;j2=1^((d>>22)&1)^s
 return struct.pack('<HH',0xf000|(s<<10)|((d>>12)&1023),(0xd000 if link else 0x9000)|(j1<<13)|(j2<<11)|((d>>1)&2047))
patched=bytearray(c);closure=json.loads((D/'RELOCATION-CLOSURE.json').read_text());expected=[(110,encode(a+110,0x4b127c,False)),(114,struct.pack('<HH',0xf8df,0x6730)),(172,encode(a+172,0x4b127c,True))]
for offset,v in expected:
 r=next(x for x in closure['bindings'] if x['offset']==offset);ck('explicit relocation '+str(offset),bytes.fromhex(r['original'])==c[offset:offset+4] and bytes.fromhex(r['resolved'])==v);patched[offset:offset+4]=v
ck('patched hash and full inequality',sha(patched)==closure['linked_candidate_sha256']=='40a8179d46fc3b662501879fcb79f79c3ffe5fb2336c6c09d52f1eff64649261' and bytes(patched)!=stock)
ck('stock exact error branch target',stock[110:114]==encode(a+110,0x4b127c,False))
ck('stock shifted tail call target',stock[180:184]==encode(a+180,0x4b127c,True))
ck('literal cell numeric binding',int.from_bytes(raw[0x514b78-base:0x514b7c-base],'little')==0x20074efc)
# Only closure arithmetic; no dynamic execution or global-name attribution.
r={'all_pass':all(x['pass'] for x in checks),'checks':checks,'scope':'Independent static byte/hash and relocation arithmetic audit; no ISA execution, SDK execution, binary extraction/redistribution, canonical admission or global name certification.'};(O/'NEMA-FINAL-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'all_pass':r['all_pass'],'checks':len(checks),'failed':[x['check'] for x in checks if not x['pass']]},indent=2))
