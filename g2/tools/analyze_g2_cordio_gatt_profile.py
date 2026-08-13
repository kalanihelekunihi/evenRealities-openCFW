#!/usr/bin/env python3
"""Authenticate G2's copied Packetcraft Cordio GATT profile object."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/packetcraft-cordio-gatt-profile-function-map.tsv';CLOSURE=ROOT/'tools/manifests/packetcraft-cordio-gatt-profile-closure.tsv';PROV=ROOT/'third_party/packetcraft-gatt-profile/PROVENANCE.json';VERIFY=ROOT/'third_party/packetcraft-gatt-profile/verify_snapshot.py'
PINS={FM:'9a504dc8f06d9a00d9565cd516235d446a495d397feda90f661a739b87f44094',CLOSURE:'95a8aa46221a8f5fb36bbcf5f1e3cf70511f73dd8b445635ca83150c054a29ae',PROV:'5733291283feec2543b8ac9d4b7fdb360107d81b2adff70e47fae2b7bbb011f9',VERIFY:'0adce5f9ff0c0b107066c370657eb9a19de8ca71f29e4b37751cfdc77a74151e'}
PHYS=(0x4B59C0,0x4B5B24);PHYS_SHA='ea73f4b2dd82c39d715ba5a707f0a8ec8a65b485db9f74ce971b15cf7b5c90da';BODY_SHA='57297c5e7efae361b5897daf562c2d051ef5fb588026ad77a6400520639e9ac2';POOL=(0x4B5ABC,0x4B5ADC);POOL_SHA='cc0e8dfd152105d90fd66b92f32c78a2afb1067abb43bd5bd1d1fe5864a96bc7';ENTRY_SHA='9dee4999d8e7796bd3db9bd748e1fa011ce756edee3c00157db515d4bc4b9a92';CALL_SHA='e44a8db4e0ae4414d9bc7b9fca194096b5425b9479116df21a92b6bb7794127f';STORED_SHA='c390fec6bfb6eb15f74528dd4a4c09797cd2d8c55f80e2eb1255a035b046e281'
PATH=0x6EF048;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\gatt\profile_gatt.c';WORDS={0x4B5ABC:0x78F53A,0x4B5AC0:0x7419F0,0x4B5AC4:0x788040,0x4B5AC8:PATH,0x4B5ACC:0x78B810,0x4B5AD0:0x72BFCC,0x4B5AD4:0x200030D0,0x4B5AD8:0x20074F38,0x4B874C:0x4B5B03,0x4B8750:0x4B5ADD};STRINGS={PATH:RETAINED,0x7419F0:' -appDiscPrint Dis Service, UUID :0x%04X',0x788040:'GattDiscover',0x78B810:'ble.gatt',0x72BFCC:'[ble.gatt] -appDiscPrint Dis Service, UUID :0x%04X'};STORED=[(0x4B874C,0x4B5B03),(0x4B8750,0x4B5ADD)]
PROVIDERS={'AppDiscFindService':0x5332B4,'AppDiscServiceChanged':0x533630,'AttsCccEnabled':0x52C628,'AttsHandleValueInd':0x533EBC,'AttsCsfGetFeatures':0x52D7C4,'memcpy':0x439BE4,'AttsCsfWriteFeatures':0x52D508}
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pd(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):o=a-BASE;e=b.find(b'\0',o);return b[o:e].decode('ascii')
def bw(b,a):
 f,s=struct.unpack_from('<HH',b,a-BASE)
 if f&0xf800!=0xf000 or s&0xd000!=0x9000:return None
 S=(f>>10)&1;j1=(s>>13)&1;j2=(s>>11)&1;i1=(~(j1^S))&1;i2=(~(j2^S))&1;imm=(S<<24)|(i1<<23)|(i2<<22)|((f&0x3ff)<<12)|((s&0x7ff)<<1)
 if imm&(1<<24):imm-=1<<25
 return a+4+imm
def oracle():
 s=importlib.util.spec_from_file_location('gatt_snapshot',VERIFY);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m.verify()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA:raise AuditError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise AuditError(f'pinned input changed: {p.name}')
 upstream=oracle()
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 starts=set();inside=set();iv=[];bodies=[]
 for r in rows:
  a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0);x=sl(b,a,z)
  if len(x)!=int(r['stock_bytes']) or sha(x)!=r['stock_sha256']:raise AuditError('stock body changed')
  starts.add(a);inside.update(range(a+2,z,2));iv.append((a,z));bodies.append(x)
 if len(rows)!=6 or sum(map(len,bodies))!=322 or sha(b''.join(bodies))!=BODY_SHA:raise AuditError('function inventory changed')
 if sha(sl(b,*PHYS))!=PHYS_SHA or sha(sl(b,*POOL))!=POOL_SHA:raise AuditError('physical object changed')
 if sha(sl(b,0x4B5B24,0x4B5C78))!='ce503526bb1f88789c398a8f70e65fee70294ca2b02ad46b735d20b27ad6cb54':raise AuditError('following object changed')
 for a,v in WORDS.items():
  if struct.unpack('<I',sl(b,a,a+4))[0]!=v:raise AuditError(f'word changed at {a:#x}')
 for a,v in STRINGS.items():
  if cstr(b,a)!=v:raise AuditError(f'string changed at {a:#x}')
 if sl(b,0x78F53A,0x78F53C)!=bytes.fromhex('0118'):raise AuditError('GATT service UUID changed')
 sys.path.insert(0,str(ROOT/'tools'));import recover_apollo_embedded_source_paths as d
 entry=[];inter=[];eb=[];ib=[]
 for o in range(0,len(b)-3,2):
  a=BASE+o;t=d._thumb_bl_target(b,a)
  if t in starts:entry.append((a,t))
  elif t in inside:inter.append((a,t))
  t=bw(b,a)
  if t in starts:eb.append((a,t))
  elif t in inside:ib.append((a,t))
 if len(entry)!=8 or pd(entry)!=ENTRY_SHA or inter or eb or ib:raise AuditError('entry topology changed')
 calls=[]
 for a,z in iv:
  for q in range(a,z-3,2):
   t=d._thumb_bl_target(b,q)
   if t is not None:calls.append((q,t))
 if len(calls)!=14 or pd(calls)!=CALL_SHA:raise AuditError('callee topology changed')
 observed={t for _,t in calls}
 if not set(PROVIDERS.values())<=observed:raise AuditError('upstream provider set changed')
 enc=starts|inside|{v|1 for v in starts|inside};raw=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0]
  if v in enc:raw.append((BASE+o,v))
 if raw!=STORED or pd(raw)!=STORED_SHA:raise AuditError('stored callback topology changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any('gatt_main.c' in x.get('path','') or 'profile_gatt' in x.get('path','') for x in overlay['sources'])
 if routed:raise AuditError('source oracle unexpectedly entered production')
 return {'surface':{'linked_functions':6,'source_owned_functions':6,'body_bytes':322,'physical_bytes':356,'direct_bl_entry_sites':8,'direct_body_calls':14,'stored_entry_pointers':2,'strict_interior_ingress':0},'upstream':{'component':'Packetcraft Cordio','source':'ble-profiles/sources/profiles/gatt/gatt_main.c','selected_release':'r20.05c','selected_commit':upstream['selected_commit'],'source_blob':'bba9a3041ce14284a0bf527934eabd01c01694d8','compatible_release_count':4,'historical_g2_generating_commit':None},'functions':[r['function'] for r in rows],'local_delta':{'function':'GattDiscover','kind':'inserted EasyLogger expansion','upstream_terminal_call':'AppDiscFindService','service_uuid':'0x1801','handle_list_length':3},'providers':{k:f'{v:#010x}' for k,v in PROVIDERS.items()},'production':{'source_admitted':True,'production_routed':routed,'ownership_bytes':0}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 Cordio GATT-profile audit: PASS')
