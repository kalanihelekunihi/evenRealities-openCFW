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
FUNCTION_MAP=ROOT/'tools/manifests/g2-ble-transport-profiles-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-ble-transport-profiles-closure.tsv';PROVENANCE=ROOT/'tools/manifests/g2-ble-transport-profiles-provenance.tsv'
SOURCE=ROOT/'components/apollo_main/core_overlay/ble_transport_profiles.c';SOURCE_PATH='components/apollo_main/core_overlay/ble_transport_profiles.c';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json';FLASH_PLAN=ROOT/'build/source/flash-plan.json'
PINS={FUNCTION_MAP:'a31155ed0cbe4e73267115dc78a7f8fcc30081f44bf601608b0ace2646a9f989',CLOSURE:'0f3497001a0d36ad8914d622a763b66e0cb7b81db0c7a0febdf3c2c50cd72c2b',PROVENANCE:'a53a7958bec483e637f0598f82fae63c2165bde4fad355b85fc280d788de89e9'}
SOURCE_PIN=(17170,'f3d21213b89cd82aa7798dc0ea8fb89ebc338842b50b8a97091ba980fada55be')
LEAF_NAMES=('open_cfw_ble_eus_process_ccc','open_cfw_ble_eus_process_message','open_cfw_ble_eus_handler_init','open_cfw_ble_eus_public_process_message','open_cfw_ble_eus_send_data','open_cfw_ble_eus_direct_send_data','open_cfw_ble_eus_write_callback','open_cfw_ble_ess_process_ccc','open_cfw_ble_ess_process_message','open_cfw_ble_ess_handler_init','open_cfw_ble_ess_public_process_message','open_cfw_ble_ess_send_data','open_cfw_ble_ess_write_callback','open_cfw_ble_efs_process_ccc','open_cfw_ble_efs_process_message','open_cfw_ble_efs_handler_init','open_cfw_ble_efs_public_process_message','open_cfw_ble_efs_send_data','open_cfw_ble_efs_write_callback','open_cfw_ble_nus_process_ccc','open_cfw_ble_nus_process_message','open_cfw_ble_nus_handler_init','open_cfw_ble_nus_public_process_message','open_cfw_ble_nus_send_data','open_cfw_ble_nus_write_callback')
LEAF_DIGEST='5a9655bbf265dddbba05af1973dd3f7faa863ffdc00c8a24889aa4b1ff3b01d3';PATCH_DIGEST='c58513379fe11707c31e2b28ada7800d770a8116ea0487204accbbf059ac78a4';BUILT_DIGEST='bb1881cf7957ac1a4560d75cb33fb43678a91db7c478a75ef2749c442a1f0a72';REGION_DIGEST='bc5d318b423f24292cdb78c06c461726a02daf9d050d814e1f4b624342fba98c'
MODULES={
 'eus':{'path':r'platform\ble\profiles\eus\profile_eus.c','path_run':0x6F5490,'path_pointer_cell':0x4BE1D4,'physical':(0x4BDE4C,0x4BE228),'physical_sha256':'59c4fc0bdb479aee0c64515a58f318f709560440ea5906121344925c4f3f349b','body_bytes':892,'body_sha256':'05f4528346de6738fec136670ac5093039ad8cd953078c4e78cef77424521609','entry_count':4,'entry_sha256':'58e59afb043d86b3510ddc80d5b72d3e27a5f1b45dae6343facc3fa68c161469','call_count':55,'call_sha256':'2b727ba0b3cf8ef21eb6315dd083a41dc05c6ec75e1f1fce1d336bc64bcaeede','stored':[(0x4B8758,0x4BDF3D),(0x4C9C5C,0x4BE14F),(0x4C9C60,0x4BDFF5)],'stored_sha256':'bfaa9a67f2d080d4e99a4c0f7a3fc58af4986434a7a09e631fd18ae41f6ae30a','send_event':0xA8,'provider_handle':0x844,'log':(0x6EEFF8,'[profile.eus]eusCb.cccdEnable ccc state = %d, connId = %d, eusCb.connId = %d')},
 'ess':{'path':r'platform\ble\profiles\ess\profile_ess.c','path_run':0x6F5444,'path_pointer_cell':0x4BE398,'physical':(0x4BE228,0x4BE3A4),'physical_sha256':'aa6109f405b2a93f5dda139e5d4c900f42ef482d633dd1acb6f69d8f230798f2','body_bytes':348,'body_sha256':'b9f57cb56734b5103b06816d661eb6ac98ab07ce9d0047d66ea5193e899c4618','entry_count':6,'entry_sha256':'7a0b07839110717b673c6f2fdbfcb5a45083c61d65ea2eea93c461ff06de8a4d','call_count':18,'call_sha256':'50af7339be5d9f8687804d44f94cd2a5d378b3b9b172f61e5a7c997d93230eb4','stored':[(0x4B875C,0x4BE2B5)],'stored_sha256':'c5bc5cd791505d3fea3b361db7e655ed23052af1e895098e2396b763e14bed79','send_event':0xA9,'provider_handle':0x864,'log':None},
 'efs':{'path':r'platform\ble\profiles\efs\profile_efs.c','path_run':0x6F53F8,'path_pointer_cell':0x4BE6A0,'physical':(0x4BE3A4,0x4BE6F0),'physical_sha256':'811f084f0fa760f10d18fba63af5c9d89302c66d91ce1a0542c5e24f9fa3b7bd','body_bytes':754,'body_sha256':'02368ef29f62cb3c9f0f7efd502403d3040ca93ec4c279cdf2b43b938c7b65ba','entry_count':4,'entry_sha256':'a931864a00d24d75c6de540e939280854dddc680c52d13ddadd2773f01aef632','call_count':47,'call_sha256':'04622b9cad600a4a7f58d72232024f4dcfdf98685345025f1ff76887e6902dcd','stored':[(0x4B8760,0x4BE487)],'stored_sha256':'9a5bd9aee413bde7c825e3db415616257be771b9ec53318d96955677d2debca7','send_event':0xAA,'provider_handle':0x884,'log':(0x6EEFA8,'[profile.efs]efsCb.cccdEnable ccc state = %d, connId = %d, efsCb.connId = %d')},
 'nus':{'path':r'platform\ble\profiles\nus\profile_nus.c','path_run':0x6F54DC,'path_pointer_cell':0x4BE9C0,'physical':(0x4BE6F0,0x4BEA04),'physical_sha256':'98a1c7a2a8221cf680e6f6ee6dede0d8235e95e224d37a873b9f95902a952707','body_bytes':704,'body_sha256':'d6a3e6767490928b71e9abbe4bcdab2aabeb591ce1bde62d124b875b11bedf45','entry_count':6,'entry_sha256':'4bd1b2d7bc50c0115ac8979311b3576dfb19e2db52aab6f11bc49e401a85ddd4','call_count':43,'call_sha256':'c565a326bed282ddc25a07aaea8f366fb833268fd1bafdb0493dd6baac913107','stored':[(0x4B8764,0x4BE7D3)],'stored_sha256':'c13be2f5c904fe93178192e9f5a07f4ada09987f45616bd18af1cbe63fa20fde','send_event':0xAB,'provider_handle':0x8A4,'log':(0x6EF098,'[profile.nus]nusCb.cccdEnable ccc state = %d, connId = %d, nusCb.connId = %d')},
}
class AuditError(RuntimeError):pass
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def jsh(x:object)->str:return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
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
 overlay=json.loads(OVERLAY.read_text())
 return {x.get('function') for x in overlay.get('relocated_leaves',[]) if x.get('source',{}).get('path')==SOURCE_PATH}==set(LEAF_NAMES)
def analyze(image:Path=IMAGE)->dict[str,Any]:
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA256:raise AuditError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise AuditError(f'pinned input changed: {p.name}')
 with FUNCTION_MAP.open(newline='',encoding='utf-8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=25 or {r['module'] for r in rows}!=set(MODULES):raise AuditError('function-map inventory changed')
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
  production_checks={'source_functions':len(chosen),'stock_replaced_bytes':len(body),'retained_literal_pool_bytes':len(phys)-len(body)}
  if metrics.get('production_routed')!='true' or metrics.get('software_functional_gap')!='false' or not metrics.get('hardware_validation','').startswith('blocked:') or any(int(metrics[k])!=v for k,v in production_checks.items()):raise AuditError(f'{name} production closure metric changed')
  reports[name]={'retained_path':x['path'],'functions':[r['function'] for r in chosen],'surface':{'linked_functions':len(chosen),'body_bytes':len(body),'physical_bytes':len(phys),'owned_noncode_bytes':len(phys)-len(body),'direct_bl_entry_sites':len(entries),'direct_body_calls':len(calls),'stored_entry_pointers':len(stored),'strict_interior_ingress':0},'protocol':{'control_block_bytes':4,'connection_event':0x12,'ccc_event':0x14,'open_event':0x27,'close_event':0x28,'send_event':x['send_event'],'provider_handle':x['provider_handle']},'ownership':'g2_local_cordio_adapter'}
 routed=production_routed()
 if not routed:raise AuditError('production BLE transport profiles are not routed')
 source=SOURCE.read_bytes()
 if (len(source),sha(source))!=SOURCE_PIN:raise AuditError('production BLE transport-profile source changed')
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH]
 if tuple(x.get('function') for x in leaves)!=LEAF_NAMES or not set(LEAF_NAMES)<=set(overlay['functions']) or jsh(leaves)!=LEAF_DIGEST:raise AuditError('production BLE transport-profile leaf closure changed')
 if any(x.get('profiles')!=['apple-clang'] or not x.get('strict_relocation_contract') or x.get('source',{}).get('license')!='GPL-3.0-only' for x in leaves):raise AuditError('production BLE transport-profile leaf policy changed')
 if sum(x['expected']['size'] for x in leaves)!=1240 or sum(len(x['relocations']) for x in leaves)!=45:raise AuditError('production BLE transport-profile compiled census changed')
 previous=282796;alignment=0
 for leaf in leaves:alignment+=leaf['expected']['offset']-previous;previous=leaf['expected']['offset']+leaf['expected']['size']
 if alignment!=10 or previous!=284046:raise AuditError('production BLE transport-profile placement changed')
 patches=[x for x in overlay['patch_sites'] if x.get('target_function') in set(LEAF_NAMES)]
 if len(patches)!=25 or jsh(patches)!=PATCH_DIGEST or sum(x['expected_size'] for x in patches)!=2698 or {x['target_function'] for x in patches}!=set(LEAF_NAMES):raise AuditError('production BLE transport-profile redirects changed')
 if any(x.get('branch')!='b_w' or x.get('profiles')!=['apple-clang'] for x in patches):raise AuditError('production BLE transport-profile redirect policy changed')
 build=json.loads(REPORT.read_text())
 if (build['overlay']['size'],build['overlay']['sha256'],build['component']['size'],build['component']['sha256'])!=(332148,'588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d',3855544,'df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc'):raise AuditError('production BLE transport-profile build pins changed')
 built=[x for x in build['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH];norm=[{'function':x['extraction']['function'],'size':x['placement']['size'],'padding_before':x['placement']['padding_before'],'offset':x['placement']['offset'],'runtime_address':x['placement']['runtime_address'],'relocation_count':x['extraction']['relocation_count']} for x in built]
 if len(built)!=25 or jsh(norm)!=BUILT_DIGEST or sum(x['size'] for x in norm)!=1240 or sum(x['padding_before'] for x in norm)!=10 or sum(x['relocation_count'] for x in norm)!=45:raise AuditError('production BLE transport-profile built closure changed')
 manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions=[x for x in main['regions'] if x.get('name','').startswith(('ble_transport_profiles_','opaque_ble_'))]
 if len(regions)!=59 or jsh(regions)!=REGION_DIGEST:raise AuditError('production BLE transport-profile manifest regions changed')
 retained=[x for x in regions if x.get('name','').startswith('opaque_ble_')]
 replaced=[x for x in regions if x.get('address_status')=='generated_source_entry_replacement']
 if len(retained)!=4 or sum(x['size'] for x in retained)!=302 or any(x.get('address_status')!='official_blob' for x in retained) or len(replaced)!=25 or sum(x['size'] for x in replaced)!=2698:raise AuditError('production BLE transport-profile stock tiling changed')
 remainder=next((x for x in main['regions'] if x.get('name')=='apollo_opaque_after_ble_transport_profiles'),None)
 if not remainder or (remainder.get('target_address'),remainder.get('size'),remainder.get('address_status'))!=(0x4BEA04,14810,'official_blob'):raise AuditError('post-profile retained Apollo region changed')
 if (main['provider']['size'],main['provider']['sha256'],manifest['package']['expected_size'],manifest['package']['expected_sha256'])!=(3855544,'df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc',4634038,'3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731'):raise AuditError('production BLE transport-profile manifest closure changed')
 plan_bytes=FLASH_PLAN.read_bytes();plan=json.loads(plan_bytes)
 if (len(plan_bytes),sha(plan_bytes))!=(3108201,'e91992690cb5766623f0b95b0928d3113ea9c0deac6d12275d55db6f12741297') or plan.get('package_sha256')!='3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731' or tuple(len(plan[k]) for k in ('flash_regions','unresolved_flash_regions','container_only_regions','protected_regions'))!=(4482,2,5,6):raise AuditError('production BLE transport-profile flash plan changed')
 return {'schema_version':1,'analysis_mode':'read-only raw-image and production-source closure; no hardware or flash operation','modules':reports,'aggregate':{'modules':4,'linked_functions':25,'body_bytes':2698,'physical_bytes':3000,'production_routed':True},'upstream_sweep':{'exact_public_symbol_hits':0,'ambiqsuite_2_5_1_profiles':['amdtpc','amdtps','amota','amsc','ancc','custss','vole'],'ambiqsuite_contains_any_module':False,'nordic_nus_api_match':False,'cordio_role':'provider framework only','third_party_source_dependency_identified':False,'historical_g2_generating_commit':None},'production':{'source_admitted':True,'production_routed':True,'source_functions':25,'compiled_text_bytes':1240,'alignment_bytes':10,'stock_replaced_bytes':2698,'retained_literal_pool_bytes':302,'strict_relocations':45,'software_functional_gap':False,'hardware_validation':'blocked','hardware_blocker':'No authorized responsive G2/EM9305 peer or captured dual-device CCC/RX/TX timing evidence is available.'}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE transport-profile audit: PASS')
