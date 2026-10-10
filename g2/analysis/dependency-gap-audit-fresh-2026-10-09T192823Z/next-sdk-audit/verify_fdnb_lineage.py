from pathlib import Path
import json,hashlib,re,zipfile,struct
O=Path(__file__).resolve().parent;D=Path('g2/analysis/iom-fdnb-stock-lineage-20261009-implementation');sha=lambda b:hashlib.sha256(b).hexdigest();b=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();base=0x437fe0;r=json.loads((D/'stock-receipts.json').read_text());checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
ck('locked package',sha(b)==r['payload_sha256'])
for x in r['ranges']:
 v=b[int(x['payload_offset'],16):int(x['payload_offset'],16)+x['size']];ck('extent '+str(x.get('label')),v.hex()==x['original_bytes_hex'] and sha(v)==x['sha256'])
ok=True;count=0
for ad,hs in re.findall(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+){1,2})\t',(D/'original-disassembly.txt').read_text(),re.M):
 a=int(ad,16);v=b''.join(int(h,16).to_bytes(2,'little') for h in hs.split());ok &= b[a-base:a-base+len(v)]==v;count+=1
ck('all serialized listing original bytes',ok and count>300)
ck('HP byte load/compare',b[0x55c57c-base:0x55c582-base]==bytes.fromhex('96f83c080028'))
op=int.from_bytes(b[0x55c582-base:0x55c584-base],'little');ck('HP zero dispatch target',op==0xd07c and 0x55c582+4+2*(op&255)==0x55c67e)
ck('service begins ordinary validation then HP',b[0x55c57a-base:0x55c582-base]==bytes.fromhex('756896f83c080028'))
ck('interrupt accumulation',b[0x55c584-base:0x55c58e-base]==bytes.fromhex('b06958ea0008c6f81880'))
ck('blocking direction validation',b[0x55cf6e-base:0x55cf76-base]==bytes.fromhex('99f81400022801d0'))
def body(s,name):
 a=re.search(r'^'+name+r'\(',s,re.M).start();i=s.index('{',a)+1;d=1
 while d:d+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
old=Path('third-party/upstream/ambiqhal-apollo510/mcu/apollo510/hal/mcu/am_hal_iom.c').read_text()
with zipfile.ZipFile('/Users/kalani/Downloads/AmbiqSuite_5.2.0.zip') as z:new=z.read(next(n for n in z.namelist() if n.endswith('/mcu/apollo510/hal/mcu/am_hal_iom.c'))).decode()
ck('complete blocking source definition identical',body(old,'am_hal_iom_spi_blocking_fullduplex')==body(new,'am_hal_iom_spi_blocking_fullduplex'))
# Bound one existing callee and direct-caller encoding candidates, no source identity assumed.
def bl(a):
 h1,h2=struct.unpack_from('<HH',b,a-base)
 if h1&0xf800!=0xf000 or h2&0xd000!=0xd000:return None
 s=(h1>>10)&1;i1=1^((h2>>13)&1)^s;i2=1^((h2>>11)&1)^s;d=(s<<24)|(i1<<23)|(i2<<22)|((h1&1023)<<12)|((h2&2047)<<1)
 return a+4+(d-(1<<25) if s else d)
ck('blocking validation callee',bl(0x55cf80)==0x55c1e0)
ck('validation extent hash',sha(b[0x55c1e0-base:0x55c286-base])=='f0fa087eaffd371b53145fb705ff4cedc7974c95e955b3a89b051ce1bd64c408')
calls=[hex(a) for a in range(0x55b000,0x55d248,2) if bl(a)==0x55c1e0]
result={'all_pass':all(x['pass'] for x in checks),'checks':checks,'validation_extent':{'start':'0x55c1e0','end':'0x55c286','bytes':166,'sha256':'f0fa087eaffd371b53145fb705ff4cedc7974c95e955b3a89b051ce1bd64c408'},'bounded_direct_BL_candidates_to_validation':calls,'scope':'Static source/body/hash/controlflow audit; candidate BL encodings need enclosing code/root classification. No new function admission or execution.'};(O/'FDNB-LINEAGE-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'all_pass':result['all_pass'],'checks':len(checks),'failed':[x['check'] for x in checks if not x['pass']],'validation_call_candidates':calls},indent=2))
