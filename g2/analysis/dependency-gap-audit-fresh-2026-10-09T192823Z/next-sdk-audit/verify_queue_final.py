from pathlib import Path
import json,hashlib,struct,re
O=Path(__file__).resolve().parent;D=Path('g2/analysis/iom-queue-offset-stock-binding-20261009-implementation');j=json.loads((D/'stock-receipts.json').read_text());b=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();base=0x437fe0;sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
ck('locked payload',sha(b)==j['payload_sha256'])
for r in j['selected_ranges']:
 a=int(r['payload_offset'],16);v=b[a:a+r['size']];ck('full range '+r['entry'],v.hex()==r['original_bytes_hex'] and sha(v)==r['sha256'])
def at(a,n):return b[a-base:a-base+n]
ck('transaction/blocking arguments',at(0x55c1e6,4)==bytes.fromhex('0d001700'))
ck('byte pause at36',at(0x55c264,4)==bytes.fromhex('95f82400'))
# Thumb16 LDR immediate: base r5, destination r0, byte-offset40.
h=int.from_bytes(at(0x55c272,2),'little');ck('word status at40',h&0xf800==0x6800 and (h>>3)&7==5 and h&7==0 and ((h>>6)&31)*4==40)
ck('queue guard truncation/zero compare',at(0x55c25e,4)==bytes.fromhex('ffb2002f'))
h=int.from_bytes(at(0x55c262,2),'little');d=h&255;d=d-256 if d&128 else d;ck('nonzero blocking skips queue checks',h&0xff00==0xd100 and 0x55c262+4+2*d==0x55c280)
ck('status mask literal',int.from_bytes(at(0x55cc10,4),'little')==0x00e0e0e0)
ck('both direct callers blocking=true',at(0x55cc62,6)==bytes.fromhex('012221005046') and at(0x55cf7a,6)==bytes.fromhex('012249460498'))
def target(a):
 h1,h2=struct.unpack('<HH',at(a,4));s=(h1>>10)&1;i1=1^((h2>>13)&1)^s;i2=1^((h2>>11)&1)^s;d=(s<<24)|(i1<<23)|(i2<<22)|((h1&1023)<<12)|((h2&2047)<<1);return a+4+(d-(1<<25) if s else d)
ck('three direct BL targets',target(0x55cc68)==target(0x55cf80)==0x55c1e0 and target(0x52e018)==0x55cf40)
ck('application queue slot stores',at(0x52dfee,2)==bytes.fromhex('0b90') and at(0x52dff2,2)==bytes.fromhex('0c90'))
ck('application transaction pointer/handle',at(0x52e014,4)==bytes.fromhex('02a96068'))
p=Path(j['search_scope']['functions_jsonl']);rs=[json.loads(x) for x in p.read_text().splitlines()];ck('metadata hash/count',sha(p.read_bytes())==j['search_scope']['sha256'] and len(rs)==7449);ck('metadata direct validator callers',{x['entry'] for x in rs if '0055c1e0' in x.get('callees',[])}=={'0055cc1c','0055cf40'})
ok=True;n=0
for ad,hs in re.findall(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+){1,2})\t',(D/'original-disassembly.txt').read_text(),re.M):
 a=int(ad,16);v=b''.join(int(h,16).to_bytes(2,'little') for h in hs.split());ok &= at(a,len(v))==v;n+=1
ck('listing original halfwords',ok and n>300)
r={'all_pass':all(x['pass'] for x in checks),'checks':checks,'scope':'Static instruction/hash/metadata verification, not execution or closed-world graph. Conditional source layout is not producer ABI proof.'};(O/'QUEUE-FINAL-INDEPENDENT-VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'all_pass':r['all_pass'],'checks':len(checks),'failed':[x['check'] for x in checks if not x['pass']]},indent=2))
