#!/usr/bin/env python3
"""Authenticate the Ambiq-derived G2 OTA adapter and G2-local Ring profile."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/g2-ble-ota-ring-profiles-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-ble-ota-ring-profiles-closure.tsv';PROV=ROOT/'third_party/ambiqsuite-amota-profile/PROVENANCE.json';VERIFY=ROOT/'third_party/ambiqsuite-amota-profile/verify_snapshot.py'
PINS={FM:'73e7ffba7d60c2f495cb87745d9d996071a3ab0b490d30ac49cb5c1018904098',CLOSURE:'525e8af452fe07c2c1cf9561616310f41bdd701f5c7eb4d0685337c76128c9dd',PROV:'bdcfac1f9e0020996dfba6bc7b9eb77ea46bb585562a4e3d15c7bb91b68ffbb0',VERIFY:'5940da878e18ace5112bbfac0874ebda42664601098aec115a705b9572f019c5'}
MODULES={
 'ota':{'path':r'platform\ble\profiles\ota\profile_ota.c','path_run':0x6F5528,'path_cell':0x4BDE08,'physical':(0x4BDB90,0x4BDE4C),'physical_sha':'603013c2916a201e4c44d3062c086706d731d3d3e27d6f56f37e153aa1057b62','body_bytes':620,'body_sha':'ee66478c1f853d30b5f6f6d704bb31f960551bd6c4380039b23d93a1167f475c','entry_count':4,'entry_sha':'9c4fb680b1794051fb7b9be3e5c60cf6ddc3e13f839324450e4b70f3d54a1e33','call_count':37,'call_sha':'145e62663b8fb720d2d7406d0c512f4393fd0915fc23784e8ba8f6fc68afb13b','stored':[(0x446CDC,0x4BDD19),(0x4B8754,0x4BDC9D)],'stored_sha':'5a86d5349a6f10a28ce905bce3a376d89e9e97e346bee316d28ed7214281f970','log':(0x721828,'[profile.ota]ccc state ind value:%d handle:%d idx:%d'),'events':[0x12,0x14,0x27,0x28,0xA0,0xA1,0xA7],'provider_handle':0x824,'providers':{0x48D8D8,0x533ED8,0x4BF99E,0x4BF9BA}},
 'ring':{'path':r'platform\ble\profiles\ring\profile_ring.c','path_run':0x6EF0E8,'path_cell':0x4C4C74,'physical':(0x4C46C0,0x4C4CEC),'physical_sha':'568c2f28253068a3c36ec4e94b71236d70879a859b5dee4d26803a8827a0c0d6','body_bytes':1446,'body_sha':'c1c4050f1d01985b66aff310a58c9caf080b01ae7e25f212784eef79517f047c','entry_count':13,'entry_sha':'b4b2c3d3d2d309019ff24637eff7181a531ef3ec4f9db3cf0fdaf78a9c7d72c1','call_count':75,'call_sha':'3322729bea78bf1320309b35ce5f60491f44d6bfca7e53dd38714a3a04d0a153','stored':[(0x4C4CD4,0x4C46D1)],'stored_sha':'57efef3ff90a3bf5e9544f883146a14cc883bee92d655dea2b6370202169e7b6','log':(0x6EF138,'_ringEnableCccd: connId=%d, CCCD handle=0x%04X, value=0x0001 (NOTIFY), flag=%d'),'events':[0x05,0x0D,0x0E,0x27,0x28,0xAC],'provider_handle':None,'providers':{0x5332B4,0x4B579C,0x539DEA,0x4BF99E,0x4BF9BA}},
}
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pd(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):o=a-BASE;e=b.find(b'\0',o);return b[o:e].decode('ascii')
def oracle():
 s=importlib.util.spec_from_file_location('amota_snapshot',VERIFY);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m.verify()
def closures():
 g=defaultdict(dict)
 with CLOSURE.open(newline='') as h:
  for r in csv.DictReader(h,delimiter='\t'):g[r['module']][r['metric']]=r['value']
 return g
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA:raise AuditError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise AuditError(f'pinned input changed: {p.name}')
 upstream=oracle();metrics=closures()
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=14 or {r['module'] for r in rows}!={'ota','ring'}:raise AuditError('function inventory changed')
 sys.path.insert(0,str(ROOT/'tools'));import recover_apollo_embedded_source_paths as d
 grouped=defaultdict(list)
 for r in rows:grouped[r['module']].append(r)
 reports={}
 for name,x in MODULES.items():
  chosen=grouped[name];starts=set();inside=set();iv=[];bodies=[]
  for r in chosen:
   a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0);v=sl(b,a,z)
   if len(v)!=int(r['stock_bytes']) or sha(v)!=r['stock_sha256']:raise AuditError(f'{name} body changed at {a:#x}')
   starts.add(a);inside.update(range(a+2,z,2));iv.append((a,z));bodies.append(v)
  body=b''.join(bodies);phys=sl(b,*x['physical'])
  if len(body)!=x['body_bytes'] or sha(body)!=x['body_sha'] or sha(phys)!=x['physical_sha']:raise AuditError(f'{name} object inventory changed')
  if cstr(b,x['path_run'])!='D:\\01_workspace\\s200_ap510b_iar_git\\'+x['path']:raise AuditError(f'{name} path changed')
  if struct.unpack('<I',sl(b,x['path_cell'],x['path_cell']+4))[0]!=x['path_run'] or cstr(b,x['log'][0])!=x['log'][1]:raise AuditError(f'{name} identity literal changed')
  entries=[];inter=[]
  for o in range(0,len(b)-3,2):
   a=BASE+o;t=d._thumb_bl_target(b,a)
   if t in starts:entries.append((a,t))
   elif t in inside:inter.append((a,t))
  if len(entries)!=x['entry_count'] or pd(entries)!=x['entry_sha'] or inter:raise AuditError(f'{name} ingress topology changed')
  calls=[]
  for a,z in iv:
   for q in range(a,z-3,2):
    t=d._thumb_bl_target(b,q)
    if t is not None:calls.append((q,t))
  if len(calls)!=x['call_count'] or pd(calls)!=x['call_sha'] or not x['providers']<={t for _,t in calls}:raise AuditError(f'{name} callee topology changed')
  encoded=starts|{a|1 for a in starts};stored=[]
  for o in range(0,len(b)-3,4):
   v=struct.unpack_from('<I',b,o)[0]
   if v in encoded:stored.append((BASE+o,v))
  if stored!=x['stored'] or pd(stored)!=x['stored_sha']:raise AuditError(f'{name} callback topology changed')
  m=metrics[name];checks={'linked_functions':len(chosen),'body_bytes':len(body),'physical_bytes':len(phys),'direct_bl_entry_sites':len(entries),'direct_body_call_sites':len(calls),'stored_entry_pointers':len(stored)}
  if m['retained_path']!=x['path'] or any(int(m[k])!=v for k,v in checks.items()):raise AuditError(f'{name} closure metrics changed')
  reports[name]={'retained_path':x['path'],'functions':[r['function'] for r in chosen],'ownership_counts':dict((o,sum(r['ownership']==o for r in chosen)) for o in ('ambiq_skeleton_derived','g2_local')),'surface':{'linked_functions':len(chosen),'body_bytes':len(body),'physical_bytes':len(phys),'owned_noncode_bytes':len(phys)-len(body),'direct_bl_entry_sites':len(entries),'direct_body_calls':len(calls),'stored_entry_pointers':len(stored),'strict_interior_ingress':0},'protocol':{'events':x['events'],'provider_handle':x['provider_handle']}}
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any(any(n in s.get('path','').lower() for n in ('profile_ota','profile_ring','ambiqsuite-amota')) for s in overlay['sources'])
 if routed:raise AuditError('evidence unexpectedly entered production')
 return {'schema_version':1,'analysis_mode':'read-only; no hardware or flash operation','modules':reports,'aggregate':{'modules':2,'linked_functions':14,'ambiq_skeleton_derived_stock_functions':4,'g2_local_stock_functions':10,'body_bytes':2066,'physical_bytes':2280},'upstream':{'ota_component':'AmbiqSuite AMOTA application skeleton','selected_release':upstream['selected_release'],'selected_commit':upstream['selected_commit'],'earliest_stable_skeleton_commit':'ca79fc6e140d25b0c596a5c87c3d311cd2710ad9','stable_release_imports':4,'historical_g2_generating_commit':None,'ring_component':None,'ring_exact_public_symbol_hits':0},'production':{'source_oracle_admitted':True,'production_routed':routed,'ownership_bytes':0}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE OTA/Ring profile audit: PASS')
