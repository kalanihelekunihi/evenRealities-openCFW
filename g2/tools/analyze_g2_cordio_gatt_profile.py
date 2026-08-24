#!/usr/bin/env python3
"""Authenticate G2's copied Packetcraft Cordio GATT profile object."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/packetcraft-cordio-gatt-profile-function-map.tsv';CLOSURE=ROOT/'tools/manifests/packetcraft-cordio-gatt-profile-closure.tsv';PROV=ROOT/'third_party/packetcraft-gatt-profile/PROVENANCE.json';VERIFY=ROOT/'third_party/packetcraft-gatt-profile/verify_snapshot.py';PROD_PROV=ROOT/'tools/manifests/packetcraft-cordio-gatt-profile-provenance.tsv'
PINS={FM:'9a504dc8f06d9a00d9565cd516235d446a495d397feda90f661a739b87f44094',CLOSURE:'6aafebbb4fddd60d260aaee49c9e6b6da65dc716a2bc9958c6ad6d5a029ba8bb',PROV:'5733291283feec2543b8ac9d4b7fdb360107d81b2adff70e47fae2b7bbb011f9',VERIFY:'0adce5f9ff0c0b107066c370657eb9a19de8ca71f29e4b37751cfdc77a74151e',PROD_PROV:'a536972173bd632e3c0c90f7dfa2a287e36e0e9b86ad1831290888426cc30d77'}
PHYS=(0x4B59C0,0x4B5B24);PHYS_SHA='ea73f4b2dd82c39d715ba5a707f0a8ec8a65b485db9f74ce971b15cf7b5c90da';BODY_SHA='57297c5e7efae361b5897daf562c2d051ef5fb588026ad77a6400520639e9ac2';POOL=(0x4B5ABC,0x4B5ADC);POOL_SHA='cc0e8dfd152105d90fd66b92f32c78a2afb1067abb43bd5bd1d1fe5864a96bc7';ENTRY_SHA='9dee4999d8e7796bd3db9bd748e1fa011ce756edee3c00157db515d4bc4b9a92';CALL_SHA='e44a8db4e0ae4414d9bc7b9fca194096b5425b9479116df21a92b6bb7794127f';STORED_SHA='c390fec6bfb6eb15f74528dd4a4c09797cd2d8c55f80e2eb1255a035b046e281'
PATH=0x6EF048;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\gatt\profile_gatt.c';WORDS={0x4B5ABC:0x78F53A,0x4B5AC0:0x7419F0,0x4B5AC4:0x788040,0x4B5AC8:PATH,0x4B5ACC:0x78B810,0x4B5AD0:0x72BFCC,0x4B5AD4:0x200030D0,0x4B5AD8:0x20074F38,0x4B874C:0x4B5B03,0x4B8750:0x4B5ADD};STRINGS={PATH:RETAINED,0x7419F0:' -appDiscPrint Dis Service, UUID :0x%04X',0x788040:'GattDiscover',0x78B810:'ble.gatt',0x72BFCC:'[ble.gatt] -appDiscPrint Dis Service, UUID :0x%04X'};STORED=[(0x4B874C,0x4B5B03),(0x4B8750,0x4B5ADD)]
PROVIDERS={'AppDiscFindService':0x5332B4,'AppDiscServiceChanged':0x533630,'AttsCccEnabled':0x52C628,'AttsHandleValueInd':0x533EBC,'AttsCsfGetFeatures':0x52D7C4,'memcpy':0x439BE4,'AttsCsfWriteFeatures':0x52D508}
SOURCE=ROOT/'components/apollo_main/core_overlay/cordio_gatt_profile.c';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
SOURCE_PATH='components/apollo_main/core_overlay/cordio_gatt_profile.c';SOURCE_PIN=(8117,'edca7a119538561bc754e61db85250ff87b853c7558ab12cbda58179ef291665')
LEAF_NAMES=('open_cfw_gatt_discover','open_cfw_gatt_value_update','open_cfw_gatt_set_service_changed_index','open_cfw_gatt_send_service_changed_indication','open_cfw_gatt_read_callback','open_cfw_gatt_write_callback')
LEAF_DIGEST='7b676574f933ef319dfa81573fbf63b6ea3867f900373891e432c12a75057983';PATCH_DIGEST='4789f8c2d1b73feb300358b1b4dda28c0fc1fa9e571319604d19be7c735b9c10';BUILT_DIGEST='6e0f91e82bb9d0113d0c3bf39081dbeee6dc9207a4fed45aa27b2802710a2a16';REGION_DIGEST='8d02d44b957cdcdd945e368021caecedc017465fbc75a477cc6403eb3c5b685b'
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def jsh(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
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
 source=SOURCE.read_bytes()
 if (len(source),sha(source))!=SOURCE_PIN:raise AuditError('production GATT-profile source changed')
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH]
 if tuple(x.get('function') for x in leaves)!=LEAF_NAMES or not set(LEAF_NAMES)<=set(overlay['functions']) or jsh(leaves)!=LEAF_DIGEST:raise AuditError('production GATT-profile leaf closure changed')
 if any(x.get('profiles')!=['apple-clang'] or not x.get('strict_relocation_contract') or x.get('source',{}).get('license')!='Apache-2.0' for x in leaves):raise AuditError('production GATT-profile leaf policy changed')
 if sum(x['expected']['size'] for x in leaves)!=254 or sum(len(x['relocations']) for x in leaves)!=10:raise AuditError('production GATT-profile compiled census changed')
 previous=191566;alignment=0
 for leaf in leaves:
  alignment+=leaf['expected']['offset']-previous;previous=leaf['expected']['offset']+leaf['expected']['size']
 if alignment!=8 or previous!=191828:raise AuditError('production GATT-profile placement changed')
 patches=[x for x in overlay['patch_sites'] if x.get('name','').startswith('replace_gatt_')]
 if len(patches)!=6 or jsh(patches)!=PATCH_DIGEST or sum(x['expected_size'] for x in patches)!=322 or {x['target_function'] for x in patches}!=set(LEAF_NAMES):raise AuditError('production GATT-profile redirect closure changed')
 if any(x.get('branch')!='b_w' or x.get('profiles')!=['apple-clang'] for x in patches):raise AuditError('production GATT-profile redirect policy changed')
 build=json.loads(REPORT.read_text())
 if (build['overlay']['size'],build['overlay']['sha256'],build['component']['size'],build['component']['sha256'])!=(197488,'a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183',3720884,'026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a'):raise AuditError('production GATT-profile build pins changed')
 built=[x for x in build['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH]
 norm=[{'function':x['extraction']['function'],'size':x['placement']['size'],'padding_before':x['placement']['padding_before'],'offset':x['placement']['offset'],'runtime_address':x['placement']['runtime_address'],'relocation_count':x['extraction']['relocation_count']} for x in built]
 if len(built)!=6 or jsh(norm)!=BUILT_DIGEST:raise AuditError('production GATT-profile built closure changed')
 manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions=[x for x in main['regions'] if x.get('name','').startswith('gatt_') or x.get('name')=='opaque_gatt_profile_literal_pool']
 if len(regions)!=17 or jsh(regions)!=REGION_DIGEST:raise AuditError('production GATT-profile manifest regions changed')
 retained={x.get('name'):x for x in main['regions'] if x.get('name') in {'apollo_opaque_after_kvdb_terminal_mode_before_gatt_profile','opaque_gatt_profile_literal_pool','apollo_opaque_after_gatt_profile_before_ota_profile'}}
 expected_retained={'apollo_opaque_after_kvdb_terminal_mode_before_gatt_profile':(4916576,21600,'official_blob'),'opaque_gatt_profile_literal_pool':(4938426,34,'official_blob'),'apollo_opaque_after_gatt_profile_before_ota_profile':(4938532,32876,'official_blob')}
 if {k:(v.get('target_address'),v.get('size'),v.get('address_status')) for k,v in retained.items()}!=expected_retained:raise AuditError('retained GATT-profile official regions changed')
 if (main['provider']['size'],main['provider']['sha256'],manifest['package']['expected_size'],manifest['package']['expected_sha256'])!=(3720884,'026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a',4499378,'03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783'):raise AuditError('production GATT-profile manifest closure changed')
 return {'surface':{'linked_functions':6,'source_owned_functions':6,'body_bytes':322,'physical_bytes':356,'direct_bl_entry_sites':8,'direct_body_calls':14,'stored_entry_pointers':2,'strict_interior_ingress':0},'upstream':{'component':'Packetcraft Cordio','source':'ble-profiles/sources/profiles/gatt/gatt_main.c','selected_release':'r20.05c','selected_commit':upstream['selected_commit'],'source_blob':'bba9a3041ce14284a0bf527934eabd01c01694d8','compatible_release_count':4,'historical_g2_generating_commit':None},'functions':[r['function'] for r in rows],'local_delta':{'function':'GattDiscover','kind':'stock-only EasyLogger expansion omitted as non-controlling diagnostics','upstream_terminal_call':'AppDiscFindService','service_uuid':'0x1801','handle_list_length':3},'providers':{k:f'{v:#010x}' for k,v in PROVIDERS.items()},'production':{'source_admitted':True,'production_routed':True,'candidate':SOURCE_PATH,'source_functions':6,'compiled_text_bytes':254,'alignment_bytes':8,'stock_replaced_bytes':322,'strict_relocations':10,'retained_literal_pool_bytes':34,'diagnostic_logging':'stock EasyLogger observability omitted; functional ATT/GATT behavior retained','software_functional_gap':False,'hardware_validation':'blocked','hardware_blocker':'No authorized physical G2/EM9305 peer or captured ATT discovery/CCCD/indication interoperability evidence is available.'}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 Cordio GATT-profile audit: PASS')
