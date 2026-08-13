#!/usr/bin/env python3
"""Authenticate the G2-local EUS/ESS/EFS/NUS Cordio profile adapters."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_SHA256='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FUNCTION_MAP=ROOT/'tools/manifests/g2-ble-transport-profiles-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-ble-transport-profiles-closure.tsv'
PINS={FUNCTION_MAP:'0adcc86274ac07ef6123500a1489ab3ec0419d3d1f380ad04f98c47689228597',CLOSURE:'dd32397928095338e045954a623d00188932260cb65af09320e5e9701be8c5a5'}
MODULES={
 'eus':{'path':r'platform\ble\profiles\eus\profile_eus.c','path_run':0x6F5490,'path_pointer_cell':0x4BE1D4,'physical':(0x4BDE4C,0x4BE228),'physical_sha256':'59c4fc0bdb479aee0c64515a58f318f709560440ea5906121344925c4f3f349b','body_bytes':800,'body_sha256':'fe07d2e133cc8bb8ae4297fe8e9e22f75c26091f3e951bbedd9f55d6a1481ca9','entry_count':4,'entry_sha256':'58e59afb043d86b3510ddc80d5b72d3e27a5f1b45dae6343facc3fa68c161469','call_count':48,'call_sha256':'7f916e8074bdf4dba49fe7a67f3eebff0e6f1db9c763b7bbc72fc88e1a13cd41','stored':[(0x4C9C5C,0x4BE14F),(0x4C9C60,0x4BDFF5)],'stored_sha256':'8dd5f5baa2d0d3d99cca76479b921b5057d5ac85dd08389665874d78ecbf6614','send_event':0xA8,'provider_handle':0x844,'log':(0x6EEFF8,'[profile.eus]eusCb.cccdEnable ccc state = %d, connId = %d, eusCb.connId = %d')},
 'ess':{'path':r'platform\ble\profiles\ess\profile_ess.c','path_run':0x6F5444,'path_pointer_cell':0x4BE398,'physical':(0x4BE228,0x4BE3A4),'physical_sha256':'aa6109f405b2a93f5dda139e5d4c900f42ef482d633dd1acb6f69d8f230798f2','body_bytes':314,'body_sha256':'30a64d9ea9cfffeeffd81dd788a95839503d81f809da3933977c24fa31952f46','entry_count':6,'entry_sha256':'7a0b07839110717b673c6f2fdbfcb5a45083c61d65ea2eea93c461ff06de8a4d','call_count':16,'call_sha256':'3350e1185d75442c8edd53cc2943c3f3e01ff9396d2dabf8dc169bac98f07410','stored':[],'stored_sha256':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','send_event':0xA9,'provider_handle':0x864,'log':None},
 'efs':{'path':r'platform\ble\profiles\efs\profile_efs.c','path_run':0x6F53F8,'path_pointer_cell':0x4BE6A0,'physical':(0x4BE3A4,0x4BE6F0),'physical_sha256':'811f084f0fa760f10d18fba63af5c9d89302c66d91ce1a0542c5e24f9fa3b7bd','body_bytes':596,'body_sha256':'9db2eae05872ba85575b526c121ad827e3b592bf5366c36e2013afb1fc6a751c','entry_count':4,'entry_sha256':'a931864a00d24d75c6de540e939280854dddc680c52d13ddadd2773f01aef632','call_count':34,'call_sha256':'330cab3ee9626d82a6cb00a42e57dde51df0efe93bdba616fcf71654af28778f','stored':[],'stored_sha256':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','send_event':0xAA,'provider_handle':0x884,'log':(0x6EEFA8,'[profile.efs]efsCb.cccdEnable ccc state = %d, connId = %d, efsCb.connId = %d')},
 'nus':{'path':r'platform\ble\profiles\nus\profile_nus.c','path_run':0x6F54DC,'path_pointer_cell':0x4BE9C0,'physical':(0x4BE6F0,0x4BEA04),'physical_sha256':'98a1c7a2a8221cf680e6f6ee6dede0d8235e95e224d37a873b9f95902a952707','body_bytes':664,'body_sha256':'c5a8a3239b9e75699db5702c15efb4f95a1d577bceefb16f9c62dab557884511','entry_count':6,'entry_sha256':'4bd1b2d7bc50c0115ac8979311b3576dfb19e2db52aab6f11bc49e401a85ddd4','call_count':40,'call_sha256':'975b906061a63abb6e1c260a1971d3feb5ed8ff34117fa3df8e0b13a1fd9731a','stored':[],'stored_sha256':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','send_event':0xAB,'provider_handle':0x8A4,'log':(0x6EF098,'[profile.nus]nusCb.cccdEnable ccc state = %d, connId = %d, nusCb.connId = %d')},
}
class AuditError(RuntimeError):pass
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def sl(b:bytes,a:int,z:int)->bytes:return b[a-BASE:z-BASE]
def pd(xs:list[tuple[int,int]])->str:return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b:bytes,a:int)->str:
 o=a-BASE;e=b.find(b'\0',o)
 if e<0:raise AuditError(f'unterminated string at {a:#x}')
 return b[o:e].decode('ascii')
def read_closure()->dict[str,dict[str,str]]:
 grouped:dict[str,dict[str,str]]=defaultdict(dict)
 with CLOSURE.open(newline='',encoding='utf-8') as h:
  for r in csv.DictReader(h,delimiter='\t'):grouped[r['module']][r['metric']]=r['value']
 return dict(grouped)
def production_routed()->bool:
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());needles=('profile_eus','profile_ess','profile_efs','profile_nus')
 return any(any(n in x.get('path','').lower() for n in needles) for x in overlay['sources'])
def analyze(image:Path=IMAGE)->dict[str,Any]:
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA256:raise AuditError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise AuditError(f'pinned input changed: {p.name}')
 with FUNCTION_MAP.open(newline='',encoding='utf-8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=21 or {r['module'] for r in rows}!=set(MODULES):raise AuditError('function-map inventory changed')
 closure=read_closure();mp:dict[str,list[dict[str,str]]]=defaultdict(list)
 for r in rows:mp[r['module']].append(r)
 sys.path.insert(0,str(ROOT/'tools'))
 spec=importlib.util.spec_from_file_location('ble_profile_thumb_decoder',ROOT/'tools/recover_apollo_embedded_source_paths.py')
 if spec is None or spec.loader is None:raise AuditError('could not load Thumb decoder')
 dec=importlib.util.module_from_spec(spec);sys.modules[spec.name]=dec;spec.loader.exec_module(dec)
 reports={}
 for name,x in MODULES.items():
  chosen=mp[name];starts={int(r['stock_start'],0) for r in chosen};inside=set();iv=[];bodies=[]
  for r in chosen:
   a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0);body=sl(b,a,z)
   if len(body)!=int(r['stock_bytes']) or sha(body)!=r['stock_sha256']:raise AuditError(f'{name} stock body changed at {a:#x}')
   if r['ownership']!='g2_local':raise AuditError(f'{name} unsupported upstream ownership claim')
   iv.append((a,z));inside.update(range(a+2,z,2));bodies.append(body)
  body=b''.join(bodies);phys=sl(b,*x['physical'])
  if len(body)!=x['body_bytes'] or sha(body)!=x['body_sha256']:raise AuditError(f'{name} body inventory changed')
  if sha(phys)!=x['physical_sha256']:raise AuditError(f'{name} physical object changed')
  retained='D:\\01_workspace\\s200_ap510b_iar_git\\'+x['path']
  if cstr(b,x['path_run'])!=retained:raise AuditError(f'{name} retained path changed')
  if struct.unpack('<I',sl(b,x['path_pointer_cell'],x['path_pointer_cell']+4))[0]!=x['path_run']:raise AuditError(f'{name} path pointer changed')
  if x['log'] and cstr(b,x['log'][0])!=x['log'][1]:raise AuditError(f'{name} CCC diagnostic changed')
  entries=[];inter=[]
  for o in range(0,len(b)-3,2):
   a=BASE+o;t=dec._thumb_bl_target(b,a)
   if t in starts:entries.append((a,t))
   elif t in inside:inter.append((a,t))
  if len(entries)!=x['entry_count'] or pd(entries)!=x['entry_sha256'] or inter:raise AuditError(f'{name} entry topology changed')
  calls=[]
  for a,z in iv:
   for q in range(a,z-3,2):
    t=dec._thumb_bl_target(b,q)
    if t is not None:calls.append((q,t))
  if len(calls)!=x['call_count'] or pd(calls)!=x['call_sha256']:raise AuditError(f'{name} callee topology changed')
  encoded=starts|{v|1 for v in starts};stored=[]
  for o in range(0,len(b)-3,4):
   v=struct.unpack_from('<I',b,o)[0]
   if v in encoded:stored.append((BASE+o,v))
  if stored!=x['stored'] or pd(stored)!=x['stored_sha256']:raise AuditError(f'{name} stored-entry topology changed')
  metrics=closure[name]
  if metrics['retained_path']!=x['path']:raise AuditError(f'{name} closure path changed')
  checks={'linked_functions':len(chosen),'body_bytes':len(body),'physical_bytes':len(phys),'direct_bl_entry_sites':len(entries),'direct_body_call_sites':len(calls),'stored_entry_pointers':len(stored)}
  if any(int(metrics[k])!=v for k,v in checks.items()):raise AuditError(f'{name} closure metric changed')
  reports[name]={'retained_path':x['path'],'functions':[r['function'] for r in chosen],'surface':{'linked_functions':len(chosen),'body_bytes':len(body),'physical_bytes':len(phys),'owned_noncode_bytes':len(phys)-len(body),'direct_bl_entry_sites':len(entries),'direct_body_calls':len(calls),'stored_entry_pointers':len(stored),'strict_interior_ingress':0},'protocol':{'control_block_bytes':4,'connection_event':0x12,'ccc_event':0x14,'open_event':0x27,'close_event':0x28,'send_event':x['send_event'],'provider_handle':x['provider_handle']},'ownership':'g2_local_cordio_adapter'}
 routed=production_routed()
 if routed:raise AuditError('profile evidence unexpectedly entered production')
 return {'schema_version':1,'analysis_mode':'read-only; no hardware or flash operation','modules':reports,'aggregate':{'modules':4,'linked_functions':sum(v['surface']['linked_functions'] for v in reports.values()),'body_bytes':sum(v['surface']['body_bytes'] for v in reports.values()),'physical_bytes':sum(v['surface']['physical_bytes'] for v in reports.values()),'production_routed':routed},'upstream_sweep':{'exact_public_symbol_hits':0,'ambiqsuite_2_5_1_profiles':['amdtpc','amdtps','amota','amsc','ancc','custss','vole'],'ambiqsuite_contains_any_module':False,'nordic_nus_api_match':False,'cordio_role':'provider framework only','third_party_source_dependency_identified':False,'historical_g2_generating_commit':None},'production':{'source_admitted':False,'production_routed':routed,'ownership_bytes':0}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE transport-profile audit: PASS')
