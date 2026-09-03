#!/usr/bin/env python3
"""Authenticate the Ambiq-derived G2 OTA adapter and G2-local Ring profile."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
sys.path.insert(0,str(ROOT/'tools'))
from apollo_artifact_consistency import (
 validate_apollo_main_artifacts, validate_region_tiling,
)
FM=ROOT/'tools/manifests/g2-ble-ota-ring-profiles-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-ble-ota-ring-profiles-closure.tsv';PROV=ROOT/'third_party/ambiqsuite-amota-profile/PROVENANCE.json';VERIFY=ROOT/'third_party/ambiqsuite-amota-profile/verify_snapshot.py';PROD_PROV=ROOT/'tools/manifests/g2-ble-ota-profile-provenance.tsv';RING_PROV=ROOT/'tools/manifests/g2-ble-ring-profile-provenance.tsv'
PINS={FM:'73e7ffba7d60c2f495cb87745d9d996071a3ab0b490d30ac49cb5c1018904098',CLOSURE:'eb5e15260d6a3c7f3e5d7e75ef29aee553e0eb7fde0fcbe7f59c745159986f88',PROV:'bdcfac1f9e0020996dfba6bc7b9eb77ea46bb585562a4e3d15c7bb91b68ffbb0',VERIFY:'5940da878e18ace5112bbfac0874ebda42664601098aec115a705b9572f019c5',PROD_PROV:'e4389060a1b0a8543015533abb703072b613f26a457c1397f71b261046084518',RING_PROV:'3b88c943c4ae2edf411e4c1a5e52ea5b34f3fc04aad91bbca97e7908a532ee75'}
MODULES={
 'ota':{'path':r'platform\ble\profiles\ota\profile_ota.c','path_run':0x6F5528,'path_cell':0x4BDE08,'physical':(0x4BDB90,0x4BDE4C),'physical_sha':'603013c2916a201e4c44d3062c086706d731d3d3e27d6f56f37e153aa1057b62','body_bytes':620,'body_sha':'ee66478c1f853d30b5f6f6d704bb31f960551bd6c4380039b23d93a1167f475c','entry_count':4,'entry_sha':'9c4fb680b1794051fb7b9be3e5c60cf6ddc3e13f839324450e4b70f3d54a1e33','call_count':37,'call_sha':'145e62663b8fb720d2d7406d0c512f4393fd0915fc23784e8ba8f6fc68afb13b','stored':[(0x446CDC,0x4BDD19),(0x4B8754,0x4BDC9D)],'stored_sha':'5a86d5349a6f10a28ce905bce3a376d89e9e97e346bee316d28ed7214281f970','log':(0x721828,'[profile.ota]ccc state ind value:%d handle:%d idx:%d'),'events':[0x12,0x14,0x27,0x28,0xA0,0xA1,0xA7],'provider_handle':0x824,'providers':{0x48D8D8,0x533ED8,0x4BF99E,0x4BF9BA}},
 'ring':{'path':r'platform\ble\profiles\ring\profile_ring.c','path_run':0x6EF0E8,'path_cell':0x4C4C74,'physical':(0x4C46C0,0x4C4CEC),'physical_sha':'568c2f28253068a3c36ec4e94b71236d70879a859b5dee4d26803a8827a0c0d6','body_bytes':1446,'body_sha':'c1c4050f1d01985b66aff310a58c9caf080b01ae7e25f212784eef79517f047c','entry_count':13,'entry_sha':'b4b2c3d3d2d309019ff24637eff7181a531ef3ec4f9db3cf0fdaf78a9c7d72c1','call_count':75,'call_sha':'3322729bea78bf1320309b35ce5f60491f44d6bfca7e53dd38714a3a04d0a153','stored':[(0x4C4CD4,0x4C46D1)],'stored_sha':'57efef3ff90a3bf5e9544f883146a14cc883bee92d655dea2b6370202169e7b6','log':(0x6EF138,'_ringEnableCccd: connId=%d, CCCD handle=0x%04X, value=0x0001 (NOTIFY), flag=%d'),'events':[0x05,0x0D,0x0E,0x27,0x28,0xAC],'provider_handle':None,'providers':{0x5332B4,0x4B579C,0x539DEA,0x4BF99E,0x4BF9BA}},
}
SOURCE=ROOT/'components/apollo_main/core_overlay/ble_ota_profile.c';RING_SOURCE=ROOT/'components/apollo_main/core_overlay/ble_ring_profile.c';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json';SOURCE_PATH='components/apollo_main/core_overlay/ble_ota_profile.c';RING_SOURCE_PATH='components/apollo_main/core_overlay/ble_ring_profile.c'
SOURCE_PIN=(9851,'e8993403f028ebaf86289aa580d7addb3418973a3990eabd91a8d63710d9fde6');LEAF_NAMES=('open_cfw_ota_process_ccc','open_cfw_ota_process_message','open_cfw_ota_write_callback','open_cfw_ota_handler_init','open_cfw_ota_disconnect','open_cfw_ota_public_process_message','open_cfw_ota_send_data')
LEAF_DIGEST='6e2b1e823e1ff5b60a2b1f61133d272d24a6b5844d176d5717d333408d5e6229';PATCH_DIGEST='0ae9d699f04930a83ec320bd88b5cc6c216a22e0f1ed27fe13fb5e35f444fb7d';BUILT_DIGEST='65a0c895173b0a0c85f8e8cabccd4310bf8ae3b46cfd3502153dd03898c519f9';REGION_DIGEST='bc52888e64b8aa03bf5f673fd642d5b4a8298b4cbba8b24303505e80de9c453a'
RING_SOURCE_PIN=(14163,'1fee6da0f14810ab0ced1103e2d0b1a593dc56661027cf8af99dc43e8b903059');RING_LEAF_NAMES=('open_cfw_ring_pack_ccc_epoch','open_cfw_ring_enable_ccc','open_cfw_ring_handler_init','open_cfw_ring_service_discover','open_cfw_ring_receive_data','open_cfw_ring_process_message','open_cfw_ring_send_data')
RING_LEAF_DIGEST='5adeccc059c3d8fd54d6d5deb67251686f989ffcc9632e043c8a2a63eaf9e547';RING_PATCH_DIGEST='0c67f235ffb2526f8cca1f1040b953a2bb0b1589cc77be63092999bb61d537d2';RING_BUILT_DIGEST='4ccbb5320cbc784867c937693ef5ff2d96e3d0e48d5dbb0742eb57a7c463fe54';RING_REGION_DIGEST='e85fccb81b854218e5cc24d0ae281af42bae019c471f3f30103f1f4ef4357804'
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def jsh(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
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
 source=SOURCE.read_bytes()
 if (len(source),sha(source))!=SOURCE_PIN:raise AuditError('production BLE OTA source changed')
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH]
 if tuple(x.get('function') for x in leaves)!=LEAF_NAMES or not set(LEAF_NAMES)<=set(overlay['functions']) or jsh(leaves)!=LEAF_DIGEST:raise AuditError('production BLE OTA leaf closure changed')
 if any(x.get('profiles')!=['apple-clang'] or not x.get('strict_relocation_contract') or x.get('source',{}).get('license')!='BSD-3-Clause' for x in leaves):raise AuditError('production BLE OTA leaf policy changed')
 if sum(x['expected']['size'] for x in leaves)!=376 or sum(len(x['relocations']) for x in leaves)!=17:raise AuditError('production BLE OTA compiled census changed')
 previous=191828;alignment=0
 for leaf in leaves:alignment+=leaf['expected']['offset']-previous;previous=leaf['expected']['offset']+leaf['expected']['size']
 if alignment!=8 or previous!=192212:raise AuditError('production BLE OTA placement changed')
 patches=[x for x in overlay['patch_sites'] if x.get('target_function') in set(LEAF_NAMES)]
 if len(patches)!=7 or jsh(patches)!=PATCH_DIGEST or sum(x['expected_size'] for x in patches)!=620 or {x['target_function'] for x in patches}!=set(LEAF_NAMES):raise AuditError('production BLE OTA redirect closure changed')
 if any(x.get('branch')!='b_w' or x.get('profiles')!=['apple-clang'] for x in patches):raise AuditError('production BLE OTA redirect policy changed')
 build=json.loads(REPORT.read_text())
 validate_apollo_main_artifacts(ROOT,AuditError,'BLE OTA/Ring profiles')
 built=[x for x in build['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH];norm=[{'function':x['extraction']['function'],'size':x['placement']['size'],'padding_before':x['placement']['padding_before'],'offset':x['placement']['offset'],'runtime_address':x['placement']['runtime_address'],'relocation_count':x['extraction']['relocation_count']} for x in built]
 if len(built)!=7 or jsh(norm)!=BUILT_DIGEST:raise AuditError('production BLE OTA built closure changed')
 manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions=[x for x in main['regions'] if ((x.get('name','').startswith('ota_') and not x.get('name','').startswith(('ota_transport_','ota_service_'))) or x.get('name')=='opaque_ota_profile_literal_pool') and x.get('address_status')!='container_only']
 if len(regions)!=19 or jsh(regions)!=REGION_DIGEST:raise AuditError('production BLE OTA manifest regions changed')
 retained={x.get('name'):x for x in main['regions'] if x.get('name')=='opaque_ota_profile_literal_pool'};expected_retained={'opaque_ota_profile_literal_pool':(4972028,80,'official_blob')}
 if {k:(v.get('target_address'),v.get('size'),v.get('address_status')) for k,v in retained.items()}!=expected_retained:raise AuditError('retained BLE OTA official regions changed')
 validate_region_tiling(main['regions'],0x4B5B24,0x4BDB90,AuditError,
                        'post-GATT multipart-transport/pair-manager corridor')
 ring_source=RING_SOURCE.read_bytes()
 if (len(ring_source),sha(ring_source))!=RING_SOURCE_PIN:raise AuditError('production BLE Ring source changed')
 ring_leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')==RING_SOURCE_PATH]
 if tuple(x.get('function') for x in ring_leaves)!=RING_LEAF_NAMES or not set(RING_LEAF_NAMES)<=set(overlay['functions']) or jsh(ring_leaves)!=RING_LEAF_DIGEST:raise AuditError('production BLE Ring leaf closure changed')
 if any(x.get('profiles')!=['apple-clang'] or not x.get('strict_relocation_contract') or x.get('source',{}).get('license')!='MIT' for x in ring_leaves):raise AuditError('production BLE Ring leaf policy changed')
 if sum(x['expected']['size'] for x in ring_leaves)!=632 or sum(len(x['relocations']) for x in ring_leaves)!=23:raise AuditError('production BLE Ring compiled census changed')
 previous=192212;alignment=0
 for leaf in ring_leaves:alignment+=leaf['expected']['offset']-previous;previous=leaf['expected']['offset']+leaf['expected']['size']
 if alignment!=8 or previous!=192852:raise AuditError('production BLE Ring placement changed')
 ring_patches=[x for x in overlay['patch_sites'] if x.get('target_function') in set(RING_LEAF_NAMES)]
 if len(ring_patches)!=7 or jsh(ring_patches)!=RING_PATCH_DIGEST or sum(x['expected_size'] for x in ring_patches)!=1446 or {x['target_function'] for x in ring_patches}!=set(RING_LEAF_NAMES):raise AuditError('production BLE Ring redirect closure changed')
 if any(x.get('branch')!='b_w' or x.get('profiles')!=['apple-clang'] for x in ring_patches):raise AuditError('production BLE Ring redirect policy changed')
 ring_built=[x for x in build['relocated_leaves'] if x.get('source',{}).get('path')==RING_SOURCE_PATH];ring_norm=[{'function':x['extraction']['function'],'size':x['placement']['size'],'padding_before':x['placement']['padding_before'],'offset':x['placement']['offset'],'runtime_address':x['placement']['runtime_address'],'relocation_count':x['extraction']['relocation_count']} for x in ring_built]
 if len(ring_built)!=7 or jsh(ring_norm)!=RING_BUILT_DIGEST:raise AuditError('production BLE Ring built closure changed')
 ring_region_names={'ring_pack_ccc_epoch_source_replacement','ring_enable_ccc_source_replacement','ring_handler_init_source_replacement','ring_service_discover_source_replacement','ring_receive_data_source_replacement','ring_process_message_source_replacement','ring_send_data_source_replacement','opaque_ring_profile_literal_pool','ring_pack_ccc_epoch_source_text','ring_enable_ccc_source_alignment','ring_enable_ccc_source_text','ring_handler_init_source_text','ring_service_discover_source_alignment','ring_service_discover_source_text','ring_receive_data_source_alignment','ring_receive_data_source_text','ring_process_message_source_alignment','ring_process_message_source_text','ring_send_data_source_text'}
 ring_regions=[x for x in main['regions'] if x.get('name') in ring_region_names]
 if len(ring_regions)!=19 or jsh(ring_regions)!=RING_REGION_DIGEST:raise AuditError('production BLE Ring manifest regions changed')
 ring_retained={x.get('name'):x for x in main['regions'] if x.get('name') in {'apollo_opaque_before_ring_profile','opaque_ring_profile_literal_pool'}};ring_expected_retained={'apollo_opaque_before_ring_profile':(4989966,8882,'official_blob'),'opaque_ring_profile_literal_pool':(5000294,134,'official_blob')}
 if {k:(v.get('target_address'),v.get('size'),v.get('address_status')) for k,v in ring_retained.items()}!=ring_expected_retained:raise AuditError('retained BLE Ring official regions changed')
 production_modules={'ota':{'candidate':SOURCE_PATH,'source_functions':7,'compiled_text_bytes':376,'alignment_bytes':8,'stock_replaced_bytes':620,'strict_relocations':17,'retained_literal_pool_bytes':80,'software_functional_gap':False,'hardware_validation':'blocked by unavailable physical evidence','hardware_blocker':'Authorized physical G2/EM9305 peer or captured OTA CCC/reset/disconnect/notification timing evidence is required for future qualification.'},'ring':{'candidate':RING_SOURCE_PATH,'source_functions':7,'compiled_text_bytes':632,'alignment_bytes':8,'stock_replaced_bytes':1446,'strict_relocations':23,'retained_literal_pool_bytes':134,'software_functional_gap':False,'hardware_validation':'blocked by unavailable physical evidence','hardware_blocker':'Authorized physical G2/EM9305 peer or captured Ring discovery/CCC/RX/TX timing evidence is required for future qualification.'}}
 return {'schema_version':1,'analysis_mode':'read-only raw-image and production-source closure; no hardware or flash operation','modules':reports,'aggregate':{'modules':2,'linked_functions':14,'ambiq_skeleton_derived_stock_functions':4,'g2_local_stock_functions':10,'body_bytes':2066,'physical_bytes':2280},'upstream':{'ota_component':'AmbiqSuite AMOTA application skeleton','selected_release':upstream['selected_release'],'selected_commit':upstream['selected_commit'],'earliest_stable_skeleton_commit':'ca79fc6e140d25b0c596a5c87c3d311cd2710ad9','stable_release_imports':4,'historical_g2_generating_commit':None,'ring_component':None,'ring_exact_public_symbol_hits':0},'production':{'source_oracle_admitted':True,'ota_production_routed':True,'ring_production_routed':True,'source_functions':14,'compiled_text_bytes':1008,'alignment_bytes':16,'stock_replaced_bytes':2066,'strict_relocations':40,'retained_literal_pool_bytes':214,'software_functional_gap':False,'hardware_validation':'blocked by unavailable physical evidence','hardware_blocker':'Authorized physical G2/EM9305 peer evidence is required for future qualification of OTA and Ring profile timing.','modules':production_modules}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE OTA/Ring profile audit: PASS')
