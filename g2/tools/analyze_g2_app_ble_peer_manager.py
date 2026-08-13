#!/usr/bin/env python3
"""Fail-closed linked-object audit for G2's BLE peer-manager adapter."""
from __future__ import annotations
import csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/g2-app-ble-peer-manager-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-app-ble-peer-manager-closure.tsv'
PINS={FM:'bd0ead977259c7b2893e6d529335284bcf29720510d608521409c705b97aa98c',CLOSURE:'8219350444a8a64185eca1f52a1dfbaa745f1c0a250d315e7717eecbcd15ab2a'}
PHYS=(0x4D8F4C,0x4D914C);PHYS_SHA='f5dd1aeb8bead102c62a66a638d0a45d4cb7bd789f3c7d6361f7932207480a4c';POOL=(0x4D910A,0x4D914C);POOL_SHA='3d67da729d7ee705ec6ac8f775e52beba3fdec564a2ca88280136ef0986b2496';BODY_SHA='81083950d25c22d6c5a1737fdb0647daf15715dbe2754618ada2c8fd6980ab21'
ENTRY_SHA='e547bf96d2638cec8ec242dcb362017ca814f4cc40b245f91c5dbaf2a1dc8a9c';CALL_SHA='9c4a73bc4de7c22e1dd3d2853aa26f58796dbc8563fbad63544c95fa6182c434'
PATH=0x6FFF4C;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_peer_mgr.c'
WORDS={0x4D9110:0x200717B0,0x4D9114:0x7313C4,0x4D9118:0x77DC2C,0x4D911C:PATH,0x4D9120:0x78C9EC,0x4D9124:0x71BCB8,0x4D9128:0x200003D8,0x4D912C:0x6F14BC,0x4D9130:0x75DB10,0x4D9134:0x6E5F38,0x4D9138:0x4A1B61,0x4D913C:0x7313F4,0x4D9140:0x71BCF0,0x4D9144:0x4A23AD,0x4D9148:0x78C9F4}
STRINGS={PATH:RETAINED,0x77DC2C:'findConnIdByAddr',0x75DB10:'AppBleMasterPeerMgrUnpairDev',0x78C9EC:'ble.mgr',0x7313C4:'Peer Address  : %02X:%02X:%02X:%02X:%02X:%02X',0x6F14BC:'Device is connected or opening (connId=%d), will close before unpairing.',0x7313F4:'Device not connected, unpairing immediately.'}
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pd(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):
 o=a-BASE;e=b.find(b'\0',o)
 if e<0:raise AuditError(f'unterminated string at {a:#x}')
 return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA:raise AuditError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise AuditError(f'pinned input changed: {p.name}')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 starts=set();inside=set();iv=[];bodies=[]
 for r in rows:
  a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0);x=sl(b,a,z)
  if len(x)!=int(r['stock_bytes']) or sha(x)!=r['stock_sha256']:raise AuditError(f"body changed: {r['function']}")
  starts.add(a);inside.update(range(a+2,z,2));iv.append((a,z));bodies.append(x)
 if len(rows)!=4 or sum(map(len,bodies))!=446 or sha(b''.join(bodies))!=BODY_SHA:raise AuditError('function inventory changed')
 if len(sl(b,*PHYS))!=512 or sha(sl(b,*PHYS))!=PHYS_SHA or sha(sl(b,*POOL))!=POOL_SHA:raise AuditError('physical object changed')
 for a,v in WORDS.items():
  if struct.unpack('<I',sl(b,a,a+4))[0]!=v:raise AuditError(f'word changed at {a:#x}')
 for a,v in STRINGS.items():
  if cstr(b,a)!=v:raise AuditError(f'string changed at {a:#x}')
 needle=struct.pack('<I',PATH);hits=[];q=b.find(needle)
 while q>=0:hits.append(BASE+q);q=b.find(needle,q+1)
 if hits!=[0x4D911C]:raise AuditError('path pointer topology changed')
 sys.path.insert(0,str(ROOT/'tools'));import recover_apollo_embedded_source_paths as d
 entry=[];inter=[]
 for o in range(0,len(b)-3,2):
  a=BASE+o;t=d._thumb_bl_target(b,a)
  if t in starts:entry.append((a,t))
  elif t in inside:inter.append((a,t))
 if len(entry)!=7 or pd(entry)!=ENTRY_SHA or inter:raise AuditError('entry topology changed')
 calls=[]
 for a,z in iv:
  for q in range(a,z-3,2):
   t=d._thumb_bl_target(b,q)
   if t is not None:calls.append((q,t))
 if len(calls)!=30 or pd(calls)!=CALL_SHA:raise AuditError('callee topology changed')
 enc=starts|{v|1 for v in starts};raw=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0]
  if v in enc:raw.append((BASE+o,v))
 if raw:raise AuditError('stored entry topology changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any('peer_manager' in x.get('path','').lower() or 'peer_mgr' in x.get('path','').lower() for x in overlay['sources'])
 if routed:raise AuditError('analysis-only peer manager entered production')
 return {'surface':{'linked_functions':4,'path_anchored_functions':2,'additional_recovered_functions':2,'body_bytes':446,'literal_pool_bytes':66,'physical_bytes':512,'direct_bl_entry_sites':7,'direct_body_calls':30,'stored_entry_pointers':0,'strict_interior_ingress':0},'identity':{'retained_path':RETAINED,'ownership':'g2_local_cordio_application_adapter','third_party_dependency':None,'historical_source_available':False},'abi':{'pending_peer_tuple_address':'0x200003d8','peer_address_bytes':6,'address_type_offset':6,'cleared_address_type':'0xff','connection_record_count':3,'connection_record_stride':48},'behavior':{'find_by_address_returns_conn_id_or_zero':True,'unpair_null_address_is_noop':True,'not_connected_path_unpairs_immediately':True,'connected_or_opening_path_closes_before_deferred_unpair':True},'cross_version':{'prior_g2_symbols':['AppMasterSecClearAddr','AppMasterSecGetAddr','AppBleMasterPeerMgrUnpairDev'],'current_delta':'adds address-to-connId lookup and close-before-unpair sequencing'},'production':{'candidate':None,'production_routed':routed,'ownership_bytes':0}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE peer-manager audit: PASS')
