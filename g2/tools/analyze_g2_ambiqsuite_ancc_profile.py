#!/usr/bin/env python3
"""Authenticate the AmbiqSuite ANCC lineage copied into G2's product tree."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/ambiqsuite-ancc-profile-function-map.tsv';CLOSURE=ROOT/'tools/manifests/ambiqsuite-ancc-profile-closure.tsv';PROV=ROOT/'third_party/ambiqsuite-ancc-profile/PROVENANCE.json';VERIFY=ROOT/'third_party/ambiqsuite-ancc-profile/verify_snapshot.py'
RUNTIME=ROOT/'components/shared/cordio/runtime_ancc_profile.c';CORE=ROOT/'components/shared/cordio/runtime_ancc_profile_core.c';CORE_H=ROOT/'components/shared/cordio/runtime_ancc_profile_core.h'
PINS={FM:'18c1a8c3d5d1cf82a8e71bbd7a85e332249958a91416b536b1c6307d0cdd51b1',CLOSURE:'3c80da6ab64131144e3bace3da5ef23ed3a0b48fc731aa957d2b722e5cb79b85',PROV:'0360bbb4e34e016688c3915428b15fdaa326e8d3fae31523982905fd673e888c',VERIFY:'5937a51d9e1874dd5d7e586a1b4866886993c294de888d3bfc574ca90f4ca94e',RUNTIME:'ea2466860609003330a537a4300ab4609432217677cf827897359f7b370cedcb',CORE:'0712eee1288f7fed6a168cc27cb81b1c5f501a30d688e778597dd2e8a2d0a156',CORE_H:'c2969dfa3070e9834007068808c335120a8be50fccc54345616696fa0726548f'}
PHYS=(0x4BEA04,0x4BF990);PHYS_SHA='5a89c723bca33d424ca99ebfdfd2ac69b567f7a09f23b0be5c98549e70758d67';BODY_SHA='fc95fcf77551c5c0153b44108bfc34d7d29e740f10d7e4a2a9c8390683f8ff06';ENTRY_SHA='c7298293655f1254c7fa10c4c9546401068e7995e59cb99b79c6a6c81d80415f';CALL_SHA='5580498eba990612a12fff9c5b0b85445bb7b5b6daf99bfaa8d712469b2eded0';STORED_SHA='06fbae0a57c10cf0b787440a1c52666e6e0206763982f461cbba8667c42c68b9'
POOLS={(0x4BF214,0x4BF228):'bdf1176096c09ff14c0b67b5176c342c9a7557e934413473eb3585cb18172fa5',(0x4BF6BE,0x4BF6C4):'2f2a4a8bde74cbdd3d000ca896160d38b7b7f61d5cab070f5fae0abba87d8ffe',(0x4BF81A,0x4BF82C):'8346b4bdd03958d4bde1eb11dce34b28594f459eee0c8b02684d1f6fda0734f0',(0x4BF8B0,0x4BF990):'e472e501bf9c58cb45e83cc0b3448cfabfb90d641ca3852a95cf43aee7e394d5'}
PATH=0x6EEEB8;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\ancc\profile_ancc.c';STORED=[(0x4BF8C0,0x4BED0F),(0x4BF8DC,0x4BEA7B)]
WORDS={0x4BF21C:PATH,0x4BF928:PATH,0x4BF8C0:0x4BED0F,0x4BF8DC:0x4BEA7B,0x4BF970:0x200695C8,0x4BF98C:0x787FC0};STRINGS={PATH:RETAINED,0x763A70:'_anccGetNextNotificationHandler',0x77A714:'_anccNotiRemoveCback',0x782560:'_anccNtfValueUpdate',0x7825B0:'_anccAttrHandler',0x77A744:'_anccResetStateMachine',0x77A75C:'APP_BleAnccSvcDiscover'}
PROVIDERS={'AppDiscFindService':0x5332B4,'AttcWriteReq':0x4B579C,'memcpy':0x439BE4,'memset':0x43C0E4}
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pd(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):o=a-BASE;e=b.find(b'\0',o);return b[o:e].decode('ascii')
def oracle():
 s=importlib.util.spec_from_file_location('ancc_snapshot',VERIFY);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m.verify()
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
 if len(rows)!=21 or sum(map(len,bodies))!=3712 or sha(b''.join(bodies))!=BODY_SHA:raise AuditError('function inventory changed')
 if sum(r['ownership']=='ambiq_derived' for r in rows)!=12 or sum(r['ownership']=='g2_local' for r in rows)!=9:raise AuditError('ownership split changed')
 if len(sl(b,*PHYS))!=3980 or sha(sl(b,*PHYS))!=PHYS_SHA:raise AuditError('physical object changed')
 for bounds,digest in POOLS.items():
  if sha(sl(b,*bounds))!=digest:raise AuditError('object pool changed')
 for a,v in WORDS.items():
  if struct.unpack('<I',sl(b,a,a+4))[0]!=v:raise AuditError(f'word changed at {a:#x}')
 for a,v in STRINGS.items():
  if cstr(b,a)!=v:raise AuditError(f'string changed at {a:#x}')
 if sl(b,0x787FC0,0x787FD0)!=bytes.fromhex('d0002d121e4b0fa4994eceb531f40579'):raise AuditError('ANCS service UUID changed')
 sys.path.insert(0,str(ROOT/'tools'));import recover_apollo_embedded_source_paths as d
 entry=[];inter=[]
 for o in range(0,len(b)-3,2):
  a=BASE+o;t=d._thumb_bl_target(b,a)
  if t in starts:entry.append((a,t))
  elif t in inside:inter.append((a,t))
 if len(entry)!=26 or pd(entry)!=ENTRY_SHA or inter:raise AuditError('entry topology changed')
 calls=[]
 for a,z in iv:
  for q in range(a,z-3,2):
   t=d._thumb_bl_target(b,q)
   if t is not None:calls.append((q,t))
 if len(calls)!=155 or pd(calls)!=CALL_SHA:raise AuditError('callee topology changed')
 observed={t for _,t in calls}
 if not set(PROVIDERS.values())<=observed:raise AuditError('provider set changed')
 raw=[]
 enc=starts|{v|1 for v in starts}
 for o in range(0,len(b)-3,4):
  v=struct.unpack_from('<I',b,o)[0]
  if v in enc:raw.append((BASE+o,v))
 if raw!=STORED or pd(raw)!=STORED_SHA:raise AuditError('stored callback topology changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')=='components/shared/cordio/runtime_ancc_profile.c']
 patches=[x for x in overlay['patch_sites'] if x.get('name','').startswith('replace_ambiqsuite_ancc_profile_')]
 routed=len(leaves)==21 and len(patches)==21
 if not routed or sum(x['expected']['size'] for x in leaves)!=11760 or sum(len(x['relocations']) for x in leaves)!=69:raise AuditError('production ANCC leaves changed')
 if sum(x['expected_size'] for x in patches)!=3712 or {x['runtime_address'] for x in patches}!=starts:raise AuditError('production ANCC routes changed')
 return {'surface':{'linked_functions':21,'source_derived_stock_functions':12,'g2_local_stock_functions':9,'body_bytes':3712,'physical_bytes':3980,'direct_bl_entry_sites':26,'direct_body_calls':155,'stored_entry_pointers':2,'strict_interior_ingress':0},'upstream':{'component':'AmbiqSuite ANCC profile','selected_release':'2.5.1','selected_commit':upstream['selected_commit'],'source_blob':'4023359bf02612b07ed95f51561e7b8e7936810c','earliest_authenticated_same_implementation_commit':'ca79fc6e140d25b0c596a5c87c3d311cd2710ad9','compatible_release_count':4,'upstream_source_definitions':17,'historical_g2_generating_commit':None},'functions':[r['function'] for r in rows],'providers':{k:f'{v:#010x}' for k,v in PROVIDERS.items()},'local_delta':{'message_service':True,'synchronization':True,'whitelist_policy':True,'easylogger':True,'central_parser_reset':True},'production':{'source_admitted':True,'production_routed':routed,'ownership_bytes':11760,'relocations':69,'hardware_validation':'deferred by project direction','hardware_blocker':'An authorized responsive G2/ANCS peer or captured live notification/control-point trace is required for future qualification.'}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 AmbiqSuite ANCC-profile audit: PASS')
