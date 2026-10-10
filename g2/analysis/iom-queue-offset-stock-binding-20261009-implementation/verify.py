from pathlib import Path
import hashlib,json,struct
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
x=json.loads((D/'stock-receipts.json').read_text());raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert sha(raw)==x['payload_sha256'];im=raw[32:]
for r in x['selected_ranges']:
 a=int(r['payload_offset'],16);b=raw[a:a+r['size']]
 assert b.hex()==r['original_bytes_hex'] and sha(b)==r['sha256']
def at(a,n):return im[a-0x438000:a-0x438000+n]
def bl(a):
 h1,h2=struct.unpack('<HH',at(a,4));assert h1&0xf800==0xf000 and h2&0xd000==0xd000
 s=(h1>>10)&1;i1=1^((h2>>13)&1)^s;i2=1^((h2>>11)&1)^s
 v=(s<<24)|(i1<<23)|(i2<<22)|((h1&0x3ff)<<12)|((h2&0x7ff)<<1)
 if s:v-=1<<25
 return a+4+v
checks={0x55c1e6:'0d00',0x55c1e8:'1700',0x55c25e:'ffb2',0x55c260:'002f',0x55c262:'0dd1',0x55c264:'95f82400',0x55c272:'a86a',0x55cc62:'0122',0x55cc64:'2100',0x55cc66:'5046',0x55cf7a:'0122',0x55cf7c:'4946',0x55cf7e:'0498',0x52dfee:'0b90',0x52dff2:'0c90',0x52e014:'02a9',0x52e016:'6068'}
for a,h in checks.items():assert at(a,len(h)//2).hex()==h
assert bl(0x55cc68)==0x55c1e0 and bl(0x55cf80)==0x55c1e0 and bl(0x52e018)==0x55cf40
rs=[json.loads(l) for l in (R/x['search_scope']['functions_jsonl']).read_text().splitlines()]
assert sha((R/x['search_scope']['functions_jsonl']).read_bytes())==x['search_scope']['sha256']
assert {r['entry'] for r in rs if '0055c1e0' in r.get('callees',[])}=={'0055cc1c','0055cf40'}
print('PASS: four stock extents, 17 byte receipts, three BL targets, exact metadata caller set; offsets +36/+40 are guarded by blocking=false')
