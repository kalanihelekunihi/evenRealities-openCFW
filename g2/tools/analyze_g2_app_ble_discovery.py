#!/usr/bin/env python3
"""Fail-closed linked-object audit for G2's BLE discovery policy."""
from __future__ import annotations
import csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/g2-app-ble-discovery-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-app-ble-discovery-closure.tsv';PINS={FM:'541e3b4220ae06994cdfabcddd4816dc6d97bd02ae94af9899e47385362d160e',CLOSURE:'7c4e21b4434a2e4fb446f21622f2d1a9dc5accaa08db75c8e47b29ebad42b728'}
PHYS=(0x5354C2,0x53634E);PHYS_SHA='b7ade1a9e7168f218fc89bfaa8882cfb66519f202570bd95b1c3e1a33111d6be';POOLS={(0x535598,0x5355E0):'442ebfc49ef794f2069e0580add105bd5abc924276171f0a0b99a67a4d1a4e45',(0x53609C,0x53634E):'9e0636ffd3a01ea31a7e447f4936cf13fbaca29e8b332405b0f67ca5d099bd91'};BODY_SHA='54039f075136827454eaf7b2eb260970352eb56a76432c66e5d22fc0a26371d2';CALL_SHA='b7bee0e3616a0cf73a3ed4dcdc45edae377291ab7b3f6be96d5be5b77f291616';STORED_SHA='6c84b02361a59c714618cb7adbddbc9e4ab5c72cce37a1a157a81e2a8b1dfdc1'
PATH=0x6F7FC4;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble_discovery.c';STRINGS={PATH:RETAINED,0x768F44:'APP_StartServiceDiscovery',0x774EAC:'APP_BleServerDiscCback',0x78A058:'ble.disc',0x74733C:'APP_DISC_INIT DmConnRole(connId) = %d',0x77DBC8:'discovery complete',0x77DC04:'APP_DISC_CFG_START',0x77DC18:'APP_DISC_CFG_CMPL'};STORED=[(0x4B821C,0x5354C3),(0x4B8748,0x5355E1),(0x5355C0,0x5354C3)]
SOURCE=ROOT/'components/apollo_main/core_overlay/app_ble_discovery.c';HEADER=ROOT/'components/apollo_main/core_overlay/app_ble_discovery.h';CONFIG=ROOT/'components/apollo_main/core_overlay/overlay.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
SOURCE_PIN=(13592,'6ea54444af63e40f19c1b0345d70dca22b37034f2efdb83c4954bc0f368f2569');HEADER_PIN=(778,'e3d76c53e8c5bbbf523f5675602dda8c60463fca63414f4ae4700fcd3b3dda93')
NAMES=('open_cfw_app_start_service_discovery','open_cfw_app_ble_server_disc_callback');PATCHES=('replace_app_ble_discovery_01','replace_app_ble_discovery_02');FUNCTIONS=((0x5354C2,0x535598),(0x5355E0,0x53609C));COMPILED=(80,436)
UNRELOCATED={'apple-clang':('dfb42545f5cc2ad1e770b0871c75ad965842209088695a8bbf011f79c7a10c19','2e338d5324dc7b9b12ab609c59d04e1d16c6afebaa54ca5351eb8156d38c1b2d'),'linux-clang':('dfb42545f5cc2ad1e770b0871c75ad965842209088695a8bbf011f79c7a10c19','ab7821cbea076569cb44e2df82757e95dbbc563d8ad70d33a07ba6af5af20c0c')}
RELOCATIONS=((0x476ACE,0x4BB07C,0x47B488,0x47B3CC,0x4BF99E,0x4BF9BA),(0x5336E0,0x4B73C4,0x4B59C0,0x53303C,0x4B73C4,0x4B73C4,0x532EB4,0x4B73C4,0x4BF82C,0x53303C,0x4B73C4,0x4B73C4,0x4C487C,0x503EA8,0x4C543E,0x53303C,0x533474))
ROUTES={'apple-clang':{'path':ROOT/'components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin','report':ROOT/'components/apollo_main/core_overlay/build/build-report.json','component':'7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6','targets':(0x4B96E8,0x458540),'text':('e659f194bc73ae81d846abc1a5c5794b2309de530de22911b25a2410ca3bb85d','9db74789e13eb1361aff034c334bcb691551dbd787e1a45d3f1edf45090fee5a')},'linux-clang':{'path':ROOT/'build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin','report':ROOT/'build/canonical-observation-g2-final97/linux-a/build-report.json','component':'dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6','targets':(0x7BC4B0,0x7BC500),'text':('d81157f116deeb42cbab344b55182f8cd7e4ec33a1b8a83915d625fccc8533be','3d611994fa87e26c0343d64e603c9666a7a1edd1e033fcc42efee084ae619f6f')}}
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pd(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):
 o=a-BASE;e=b.find(b'\0',o)
 if e<0:raise AuditError(f'unterminated string at {a:#x}')
 return b[o:e].decode('ascii')
def _relocation_targets(rows):return tuple(r.get('target_address',r.get('target_function')) for r in rows)
def validate_production():
 for path,pin,label in ((SOURCE,SOURCE_PIN,'source'),(HEADER,HEADER_PIN,'header')):
  raw=path.read_bytes()
  if (len(raw),sha(raw))!=pin:raise AuditError(f'BLE discovery production {label} changed')
 config=json.loads(CONFIG.read_text());leaves={x.get('function'):x for x in config.get('relocated_leaves',[]) if x.get('function') in NAMES}
 if set(leaves)!=set(NAMES):raise AuditError('BLE discovery production leaf inventory changed')
 for index,name in enumerate(NAMES):
  leaf=leaves[name]
  for profile,record in (('apple-clang',leaf),('linux-clang',leaf.get('toolchain_profiles',{}).get('linux-clang',{}))):
   expected=record.get('expected',{})
   if (expected.get('size'),expected.get('unrelocated_sha256'))!=(COMPILED[index],UNRELOCATED[profile][index]) or _relocation_targets(record.get('relocations',[]))!=RELOCATIONS[index]:raise AuditError(f'BLE discovery production pins changed: {profile}/{name}')
  if leaf.get('profiles')!=['apple-clang','linux-clang'] or leaf.get('strict_relocation_contract') is not True or leaf.get('source',{}).get('sha256')!=SOURCE_PIN[1] or leaf.get('toolchain_profiles',{}).get('linux-clang',{}).get('reviewed_version_prefix')!='Homebrew clang version 22.1.8':raise AuditError(f'BLE discovery profile contract changed: {name}')
 patches={x.get('name'):x for x in config.get('patch_sites',[]) if x.get('name') in PATCHES}
 if set(patches)!=set(PATCHES):raise AuditError('BLE discovery patch inventory changed')
 for patch_name,name,bounds in zip(PATCHES,NAMES,FUNCTIONS):
  patch=patches[patch_name]
  if patch.get('runtime_address')!=bounds[0] or patch.get('expected_size')!=bounds[1]-bounds[0] or patch.get('target_function')!=name or patch.get('profiles')!=['apple-clang','linux-clang']:raise AuditError(f'BLE discovery patch contract changed: {patch_name}')
 manifest=json.loads(MANIFEST.read_text())['component_overrides']['apollo_main']
 for start,_end in FUNCTIONS:
  offset=start-BASE;owners=[r for r in manifest['regions'] if r.get('file_offset',-1)<=offset<r.get('file_offset',-1)+r.get('size',0)]
  if len(owners)!=1 or owners[0].get('address_status') not in {'generated_source_entry_replacement','generated_source_data_replacement'}:raise AuditError('BLE discovery manifest ownership changed')
 for profile,route in ROUTES.items():
  component=route['path'].read_bytes()
  if len(component)!=3956672 or sha(component)!=route['component']:raise AuditError(f'{profile} BLE discovery component changed')
  report=json.loads(route['report'].read_text());built={x.get('extraction',{}).get('function'):x.get('extraction',{}) for x in report.get('relocated_leaves',[]) if x.get('extraction',{}).get('function') in NAMES}
  if set(built)!=set(NAMES):raise AuditError(f'{profile} BLE discovery build inventory changed')
  for index,(bounds,target,text_digest) in enumerate(zip(FUNCTIONS,route['targets'],route['text'])):
   replacement=sl(component,*bounds)
   if apollo_overlay.decode_thumb_branch(bounds[0],replacement[:4],link=False)!=target or replacement[4:]!=b'\x00\xbf'*((len(replacement)-4)//2):raise AuditError(f'{profile} BLE discovery redirect changed')
   extraction=built[NAMES[index]]
   if extraction.get('size')!=COMPILED[index] or extraction.get('unrelocated_sha256')!=UNRELOCATED[profile][index] or extraction.get('relocation_count')!=len(RELOCATIONS[index]):raise AuditError(f'{profile} BLE discovery build receipt changed')
   if sha(sl(component,target,target+COMPILED[index]))!=text_digest:raise AuditError(f'{profile} BLE discovery routed text changed')
 validate_apollo_main_artifacts(ROOT,AuditError,'production BLE discovery')
 return {'candidate':str(SOURCE.relative_to(ROOT)),'header':str(HEADER.relative_to(ROOT)),'production_routed':True,'ownership_bytes':2962,'source_inventory_available':True,'source_functions':2,'compiled_text_bytes':{'apple-clang':516,'linux-clang':516},'alignment_bytes':{'apple-clang':0,'linux-clang':0},'strict_relocations':23,'stock_body_bytes_displaced':2962,'retained_stock_noncode_bytes':762,'profiles_verified':['apple-clang','linux-clang'],'software_functional_gap':False,'hardware_validation':'blocked by unavailable physical evidence','hardware_evidence_required':['authorized paired phone and ring traces proving role-aware database-hash, GATT, Ring, optional ANCS, configuration, failure, and completion sequencing','authorized disconnect/reconnect trace proving discovery attempt state is reset without stale handles'],'hardware_operations':[]}
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
 return {'surface':{'linked_functions':2,'body_bytes':2962,'literal_pool_bytes':762,'physical_bytes':3724,'direct_bl_entry_sites':0,'direct_body_calls':179,'stored_entry_pointers':3,'strict_interior_ingress':0},'identity':{'retained_path':RETAINED,'ownership':'g2_local_cordio_discovery_policy','third_party_dependency':None,'historical_source_available':False},'behavior':{'states':list(range(9)),'role_aware':True,'services':['database hash','GATT','Ring','ANCS'],'security_gate':True,'configuration_phase':True,'completion_callback':True},'cross_version':{'same_named_function_sizes':[214,2748],'qualification':'prior G2 image authenticates exact names and stable two-function topology; current bytes are independently pinned'},'production':validate_production()}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 BLE discovery audit: PASS')
