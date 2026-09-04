#!/usr/bin/env python3
"""Fail-closed linked-object audit for G2's BLE peer-manager adapter."""
from __future__ import annotations
import csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/g2-app-ble-peer-manager-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-app-ble-peer-manager-closure.tsv'
PINS={FM:'bd0ead977259c7b2893e6d529335284bcf29720510d608521409c705b97aa98c',CLOSURE:'4880d65b85f0fe4cf028681e3e9342b090c3cd0f843d54cde2a670241ff9f2e2'}
PHYS=(0x4D8F4C,0x4D914C);PHYS_SHA='f5dd1aeb8bead102c62a66a638d0a45d4cb7bd789f3c7d6361f7932207480a4c';POOL=(0x4D910A,0x4D914C);POOL_SHA='3d67da729d7ee705ec6ac8f775e52beba3fdec564a2ca88280136ef0986b2496';BODY_SHA='81083950d25c22d6c5a1737fdb0647daf15715dbe2754618ada2c8fd6980ab21'
ENTRY_SHA='e547bf96d2638cec8ec242dcb362017ca814f4cc40b245f91c5dbaf2a1dc8a9c';CALL_SHA='9c4a73bc4de7c22e1dd3d2853aa26f58796dbc8563fbad63544c95fa6182c434'
PATH=0x6FFF4C;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_peer_mgr.c'
WORDS={0x4D9110:0x200717B0,0x4D9114:0x7313C4,0x4D9118:0x77DC2C,0x4D911C:PATH,0x4D9120:0x78C9EC,0x4D9124:0x71BCB8,0x4D9128:0x200003D8,0x4D912C:0x6F14BC,0x4D9130:0x75DB10,0x4D9134:0x6E5F38,0x4D9138:0x4A1B61,0x4D913C:0x7313F4,0x4D9140:0x71BCF0,0x4D9144:0x4A23AD,0x4D9148:0x78C9F4}
STRINGS={PATH:RETAINED,0x77DC2C:'findConnIdByAddr',0x75DB10:'AppBleMasterPeerMgrUnpairDev',0x78C9EC:'ble.mgr',0x7313C4:'Peer Address  : %02X:%02X:%02X:%02X:%02X:%02X',0x6F14BC:'Device is connected or opening (connId=%d), will close before unpairing.',0x7313F4:'Device not connected, unpairing immediately.'}
SOURCE=ROOT/'components/apollo_main/core_overlay/app_ble_peer_manager.c';HEADER=ROOT/'components/apollo_main/core_overlay/app_ble_peer_manager.h';CONFIG=ROOT/'components/apollo_main/core_overlay/overlay.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
SOURCE_PIN=(7586,'067309c4726d1c396c953858fb7cbe55b27c4db0f7b0f814d20f2e8329abed69');HEADER_PIN=(433,'5d2178ef7d7cf69806c447b536c819659da9d48241ef0ceee8d4bce3b580b83a')
NAMES=('open_cfw_app_ble_peer_manager_find_conn_id_by_addr','open_cfw_app_master_sec_clear_addr','open_cfw_app_master_sec_get_addr','open_cfw_app_ble_master_peer_mgr_unpair_dev')
PATCHES=tuple(f'replace_app_ble_peer_manager_{i:02d}' for i in range(1,5));FUNCTIONS=((0x4D8F4C,0x4D8FF6),(0x4D8FF6,0x4D900C),(0x4D900C,0x4D9010),(0x4D9010,0x4D910A))
COMPILED=(98,42,10,176);UNRELOCATED=('d2b5e19a1ae43641910c09088e18720d4f5cf5fef713a65612836a811a43eb06','9f066f4c9d504af28d63d3c95e3b5b4fa68fe2b67601ece95e475b9222527cf6','3287056adbb922831da6ee5690013f38a70cafb83c0ecfa9ab4d744cb31a0fb6','740829ede1f3200012adab17922d09ed50725299047fea84b6774461f462ff21')
RELOCATIONS=((0x4B6EEA,0x4D294A,0x4B6EEA,0x4D294A,0x4B6EEA,0x4D294A),(),(),(0x4A22E8,NAMES[0],0x4A2300,0x476ACE,0x4A1FC4,0x4A2168,0x4A2300,0x476ACE,0x476ACE,0x4A2068,0x4A1F38))
ROUTES={
 'apple-clang':{'path':ROOT/'components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin','report':ROOT/'components/apollo_main/core_overlay/build/build-report.json','component':'7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6','targets':(0x457958,0x4C49C8,0x4D10C8,0x48FEA0),'text':('7e8a07058b3ca33b28ebd0f9cca2af2ca3915730df250e6a19dea9dbfeb8063a','9f066f4c9d504af28d63d3c95e3b5b4fa68fe2b67601ece95e475b9222527cf6','3287056adbb922831da6ee5690013f38a70cafb83c0ecfa9ab4d744cb31a0fb6','e693fddd170feebedbc3a0c19a346adec9d58ea59a55b83296b1060a69cc7667')},
 'linux-clang':{'path':ROOT/'build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin','report':ROOT/'build/canonical-observation-g2-final97/linux-a/build-report.json','component':'dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6','targets':(0x7BC360,0x7BC3C4,0x7BC3F0,0x7BC400),'text':('95e0a1f4ca096b0819d40bedf6cde8deef67d6a98a96ff3dfbf0a4d75775c7e6','9f066f4c9d504af28d63d3c95e3b5b4fa68fe2b67601ece95e475b9222527cf6','3287056adbb922831da6ee5690013f38a70cafb83c0ecfa9ab4d744cb31a0fb6','35fc96c6b7ddad423fa38338a3315727caeb367427909470b952cf5146298f0f')},
}
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pd(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):
 o=a-BASE;e=b.find(b'\0',o)
 if e<0:raise AuditError(f'unterminated string at {a:#x}')
 return b[o:e].decode('ascii')
def _relocation_targets(rows):
 return tuple(r.get('target_address',r.get('target_function')) for r in rows)
def validate_production():
 for path,pin,label in ((SOURCE,SOURCE_PIN,'source'),(HEADER,HEADER_PIN,'header')):
  raw=path.read_bytes()
  if (len(raw),sha(raw))!=pin:raise AuditError(f'BLE peer-manager production {label} changed')
 config=json.loads(CONFIG.read_text());leaves={x.get('function'):x for x in config.get('relocated_leaves',[]) if x.get('function') in NAMES}
 if set(leaves)!=set(NAMES):raise AuditError('BLE peer-manager production leaf inventory changed')
 for index,name in enumerate(NAMES):
  leaf=leaves[name];linux=leaf.get('toolchain_profiles',{}).get('linux-clang',{})
  for record in (leaf,linux):
   expected=record.get('expected',{})
   if (expected.get('size'),expected.get('unrelocated_sha256'))!=(COMPILED[index],UNRELOCATED[index]) or _relocation_targets(record.get('relocations',[]))!=RELOCATIONS[index]:raise AuditError(f'BLE peer-manager production pins changed: {name}')
  if leaf.get('profiles')!=['apple-clang','linux-clang'] or leaf.get('strict_relocation_contract') is not True or leaf.get('source',{}).get('sha256')!=SOURCE_PIN[1] or linux.get('reviewed_version_prefix')!='Homebrew clang version 22.1.8':raise AuditError(f'BLE peer-manager profile contract changed: {name}')
 patches={x.get('name'):x for x in config.get('patch_sites',[]) if x.get('name') in PATCHES}
 if set(patches)!=set(PATCHES):raise AuditError('BLE peer-manager patch inventory changed')
 for patch_name,name,bounds in zip(PATCHES,NAMES,FUNCTIONS):
  patch=patches[patch_name]
  if patch.get('runtime_address')!=bounds[0] or patch.get('expected_size')!=bounds[1]-bounds[0] or patch.get('target_function')!=name or patch.get('profiles')!=['apple-clang','linux-clang']:raise AuditError(f'BLE peer-manager patch contract changed: {patch_name}')
 manifest=json.loads(MANIFEST.read_text())['component_overrides']['apollo_main']
 for start,_end in FUNCTIONS:
  offset=start-BASE;owners=[r for r in manifest['regions'] if r.get('file_offset',-1)<=offset<r.get('file_offset',-1)+r.get('size',0)]
  if len(owners)!=1 or owners[0].get('address_status') not in {'generated_source_entry_replacement','generated_source_data_replacement'}:raise AuditError('BLE peer-manager manifest ownership changed')
 for profile,route in ROUTES.items():
  component=route['path'].read_bytes()
  if len(component)!=3956672 or sha(component)!=route['component']:raise AuditError(f'{profile} BLE peer-manager component changed')
  report=json.loads(route['report'].read_text());built={x.get('extraction',{}).get('function'):x.get('extraction',{}) for x in report.get('relocated_leaves',[]) if x.get('extraction',{}).get('function') in NAMES}
  if set(built)!=set(NAMES):raise AuditError(f'{profile} BLE peer-manager build inventory changed')
  for index,(bounds,target,text_digest) in enumerate(zip(FUNCTIONS,route['targets'],route['text'])):
   replacement=sl(component,*bounds)
   if apollo_overlay.decode_thumb_branch(bounds[0],replacement[:4],link=False)!=target or replacement[4:]!=b'\x00\xbf'*((len(replacement)-4)//2):raise AuditError(f'{profile} BLE peer-manager redirect changed')
   extraction=built[NAMES[index]]
   if extraction.get('size')!=COMPILED[index] or extraction.get('unrelocated_sha256')!=UNRELOCATED[index] or extraction.get('relocation_count')!=len(RELOCATIONS[index]):raise AuditError(f'{profile} BLE peer-manager build receipt changed')
   if sha(sl(component,target,target+COMPILED[index]))!=text_digest:raise AuditError(f'{profile} BLE peer-manager routed text changed')
 validate_apollo_main_artifacts(ROOT,AuditError,'production BLE peer-manager')
 return {'candidate':str(SOURCE.relative_to(ROOT)),'header':str(HEADER.relative_to(ROOT)),'production_routed':True,'ownership_bytes':446,'source_inventory_available':True,'source_functions':4,'compiled_text_bytes':{'apple-clang':326,'linux-clang':326},'alignment_bytes':{'apple-clang':8,'linux-clang':12},'strict_relocations':17,'stock_body_bytes_displaced':446,'retained_stock_noncode_bytes':66,'profiles_verified':['apple-clang','linux-clang'],'software_functional_gap':False,'hardware_validation':'blocked by unavailable physical evidence','hardware_evidence_required':['authorized bonded G2/peer trace proving active/opening-peer disconnect completes deferred unpair and permits a fresh pairing','authorized disconnected-peer G2 trace proving immediate address-based unpair clears persistence without starting a connection'],'hardware_operations':[]}
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
 return {'surface':{'linked_functions':4,'path_anchored_functions':2,'additional_recovered_functions':2,'body_bytes':446,'literal_pool_bytes':66,'physical_bytes':512,'direct_bl_entry_sites':7,'direct_body_calls':30,'stored_entry_pointers':0,'strict_interior_ingress':0},'identity':{'retained_path':RETAINED,'ownership':'g2_local_cordio_application_adapter','third_party_dependency':None,'historical_source_available':False},'abi':{'pending_peer_tuple_address':'0x200003d8','peer_address_bytes':6,'address_type_offset':6,'cleared_address_type':'0xff','connection_record_count':3,'connection_record_stride':48},'behavior':{'find_by_address_returns_conn_id_or_zero':True,'unpair_null_address_is_noop':True,'not_connected_path_unpairs_immediately':True,'connected_or_opening_path_closes_before_deferred_unpair':True},'cross_version':{'prior_g2_symbols':['AppMasterSecClearAddr','AppMasterSecGetAddr','AppBleMasterPeerMgrUnpairDev'],'current_delta':'adds address-to-connId lookup and close-before-unpair sequencing'},'production':validate_production()}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE peer-manager audit: PASS')
