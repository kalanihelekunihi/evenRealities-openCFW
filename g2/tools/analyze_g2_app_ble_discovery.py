#!/usr/bin/env python3
"""Fail-closed linked-object audit for G2's BLE discovery policy."""
from __future__ import annotations
import csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/g2-app-ble-discovery-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-app-ble-discovery-closure.tsv';PINS={FM:'541e3b4220ae06994cdfabcddd4816dc6d97bd02ae94af9899e47385362d160e',CLOSURE:'624efe92ae72aa64664bee8a3771d6db7a04f910ccd3daac3c98cada1c7d1c91'}
PHYS=(0x5354C2,0x53634E);PHYS_SHA='b7ade1a9e7168f218fc89bfaa8882cfb66519f202570bd95b1c3e1a33111d6be';POOLS={(0x535598,0x5355E0):'442ebfc49ef794f2069e0580add105bd5abc924276171f0a0b99a67a4d1a4e45',(0x53609C,0x53634E):'9e0636ffd3a01ea31a7e447f4936cf13fbaca29e8b332405b0f67ca5d099bd91'};BODY_SHA='54039f075136827454eaf7b2eb260970352eb56a76432c66e5d22fc0a26371d2';CALL_SHA='b7bee0e3616a0cf73a3ed4dcdc45edae377291ab7b3f6be96d5be5b77f291616';STORED_SHA='6c84b02361a59c714618cb7adbddbc9e4ab5c72cce37a1a157a81e2a8b1dfdc1'
PATH=0x6F7FC4;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_discovery.c';STRINGS={PATH:RETAINED,0x768F44:'APP_StartServiceDiscovery',0x774EAC:'APP_BleServerDiscCback',0x78A058:'ble.disc',0x74733C:'APP_DISC_INIT DmConnRole(connId) = %d',0x77DBC8:'discovery complete',0x77DC04:'APP_DISC_CFG_START',0x77DC18:'APP_DISC_CFG_CMPL'};STORED=[(0x4B821C,0x5354C3),(0x4B8748,0x5355E1),(0x5355C0,0x5354C3)]
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
 if len(rows)!=2 or sum(map(len,bodies))!=2962 or sha(b''.join(bodies))!=BODY_SHA:raise AuditError('function inventory changed')
 if len(sl(b,*PHYS))!=3724 or sha(sl(b,*PHYS))!=PHYS_SHA:raise AuditError('physical object changed')
 for bounds,digest in POOLS.items():
  if sha(sl(b,*bounds))!=digest:raise AuditError('literal pool changed')
 if sha(sl(b,0x53634E,0x5363AE))!='e9fbe9a104896249e6a859995592f43f3d54407b396bb96e4320102c4ff405a8':raise AuditError('following object changed')
 for a,v in STRINGS.items():
  if cstr(b,a)!=v:raise AuditError(f'string changed at {a:#x}')
 needle=struct.pack('<I',PATH);hits=[];q=b.find(needle)
 while q>=0:hits.append(BASE+q);q=b.find(needle,q+1)
 if hits!=[0x5355CC,0x5360A8]:raise AuditError('path pointer topology changed')
 sys.path.insert(0,str(ROOT/'tools'));import recover_apollo_embedded_source_paths as d
 entry=[];inter=[]
 for o in range(0,len(b)-3,2):
  a=BASE+o;t=d._thumb_bl_target(b,a)
  if t in starts:entry.append((a,t))
  elif t in inside:inter.append((a,t))
 if entry or inter:raise AuditError('direct ingress changed')
 calls=[]
 for a,z in iv:
  for q in range(a,z-3,2):
   t=d._thumb_bl_target(b,q)
   if t is not None:calls.append((q,t))
 if len(calls)!=179 or pd(calls)!=CALL_SHA:raise AuditError('callee topology changed')
 enc=starts|{v|1 for v in starts};raw=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0]
  if v in enc:raw.append((BASE+o,v))
 if raw!=STORED or pd(raw)!=STORED_SHA:raise AuditError('stored ingress changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any('ble_discovery' in x.get('path','').lower() for x in overlay['sources'])
 if routed:raise AuditError('analysis-only discovery object entered production')
 return {'surface':{'linked_functions':2,'body_bytes':2962,'literal_pool_bytes':762,'physical_bytes':3724,'direct_bl_entry_sites':0,'direct_body_calls':179,'stored_entry_pointers':3,'strict_interior_ingress':0},'identity':{'retained_path':RETAINED,'ownership':'g2_local_cordio_discovery_policy','third_party_dependency':None,'historical_source_available':False},'behavior':{'states':list(range(9)),'role_aware':True,'services':['database hash','GATT','Ring','ANCS'],'security_gate':True,'configuration_phase':True,'completion_callback':True},'cross_version':{'same_named_function_sizes':[214,2748],'qualification':'prior G2 image authenticates exact names and stable two-function topology; current bytes are independently pinned'},'production':{'candidate':None,'production_routed':routed,'ownership_bytes':0}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE discovery audit: PASS')
