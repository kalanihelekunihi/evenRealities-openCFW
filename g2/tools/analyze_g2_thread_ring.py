#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for thread_ring.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_dashboard_watchface_manager as d
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from analyze_g2_thread_ble_production import wide_branch_target
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-thread-ring-function-map.tsv';PM=ROOT/'tools/manifests/g2-thread-ring-provider-map.tsv';CL=ROOT/'tools/manifests/g2-thread-ring-closure.tsv'
SOURCE=ROOT/'components/apollo_main/core_overlay/thread_ring.c';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json';SOURCE_MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json';PACKAGE=ROOT/'build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin';FLASH_PLAN=ROOT/'build/source/flash-plan.json'
PINS={FM:'d9de48f2ee825b6a21c1fb42dd566e681f5f44f0a2d98641c2cfe22f2e4485db',PM:'d01cf53705f3e2c4f7a1a42ba12aff429458727d5543223826e6bd46980e8ad7',CL:'ae93e2972d4738e4d88c94ee86ecc177d0b601ecc472f3fc7d52fae2a7ebb71b'}
SOURCE_SHA='14f72d62baa6eff68a019840d2673019e7c5afe4a3e48b004ebee402e39c1d18'
SOURCE_FUNCTIONS=('open_cfw_thread_ring_init_hook','open_cfw_thread_ring_queue_init','open_cfw_thread_ring_resource_hook','open_cfw_thread_ring_state_enter','open_cfw_thread_ring_state_ready','open_cfw_thread_ring_message_handler','open_cfw_thread_ring_enable_touch','open_cfw_thread_ring_disable_touch','open_cfw_thread_ring_enable_pair','open_cfw_thread_ring_exit','open_cfw_thread_ring_send_event','open_cfw_thread_ring_record_send','open_cfw_thread_ring_send_message','open_cfw_thread_ring_event_handler','open_cfw_thread_ring_entry','open_cfw_thread_ring_create','open_cfw_thread_ring_terminate')
SOURCE_OFFSETS=(253132,253136,253176,253180,253188,253196,253356,253404,253412,253416,253456,253476,253628,253640,253924,253968,254020)
SOURCE_SIZES=(2,38,2,6,6,158,48,6,4,38,20,150,10,282,44,52,28)
PATCH_FUNCTIONS=('open_cfw_thread_ring_entry','open_cfw_thread_ring_queue_init','open_cfw_thread_ring_state_enter','open_cfw_thread_ring_state_ready','open_cfw_thread_ring_create','open_cfw_thread_ring_terminate','open_cfw_thread_ring_message_handler','open_cfw_thread_ring_enable_touch','open_cfw_thread_ring_disable_touch','open_cfw_thread_ring_enable_pair','open_cfw_thread_ring_event_handler','open_cfw_thread_ring_exit','open_cfw_thread_ring_send_event','open_cfw_thread_ring_send_message','open_cfw_thread_ring_record_send')
F=((0x4C4CEC,0x4C4D64),(0x4C4D64,0x4C4D66),(0x4C4D66,0x4C4D8E),(0x4C4D8E,0x4C4D90),(0x4C4D90,0x4C4D9A),(0x4C4D9A,0x4C4DA4),(0x4C4DA4,0x4C4DD0),(0x4C4DD0,0x4C4DE8),(0x4C4DE8,0x4C4EE4),(0x4C4EE4,0x4C4FE4),(0x4C4FE4,0x4C5032),(0x4C5032,0x4C507E),(0x4C507E,0x4C53A6),(0x4C53A6,0x4C543E),(0x4C543E,0x4C548C),(0x4C548C,0x4C549C),(0x4C549C,0x4C5632))
PHYS=(0x4C4CEC,0x4C5734);POOL=(0x4C5632,0x4C5734);PATH=0x7074F8;CELL=0x4C563C
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490E2,0x4491FE,0x449238,0x4492C2,0x449376,0x449A32,0x449ABE,0x449B3C,0x449BEC};FREERTOS={0x5FA0A4};IAR={0x439BE4,0x43C0E4};HEAP={0x474CD2,0x474D16};RING={0x472244,0x4722D8,0x472362,0x472378,0x4723D6,0x472426,0x47243A,0x472546,0x472630,0x472988};EVENT={0x47697E,0x476ACE};FIRST={0x46C630,0x46EFD8,0x4C9B86,0x4C9BE2,0x4C9C3C}
STORED=[(0x472C64,0x4C4FE4),(0x472C68,0x4C4EE4),(0x4A26D8,0x4C4EE4),(0x4A3500,0x4C4EE4),(0x4C5650,0x4C4CEC),(0x4C56AC,0x4C5032),(0x4C56B0,0x4C4EE4),(0x794121,0x4C4DA4)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstr(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text());kernel=json.loads((ROOT/'third_party/freertos-kernel/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or cms['upstreams']['cmsis_5']['selected_commit']!='2b7495b8535bdcb306dac29b9ded4cfb679d7e5c' or kernel['upstream']['selected_commit']!='def7d2df2b0506d3d249334974f51e427c17a41c' or 'deff9ab509341f264addbd3c8ada533678591905' not in (ROOT/'third_party/tlsf/README.openCFW.md').read_text():raise c.AuditError('provider provenance changed')
 if 'ring\tphysical_interval\t[0x004C46C0,0x004C4CEC)' not in (ROOT/'tools/manifests/g2-ble-ota-ring-profiles-closure.tsv').read_text():raise c.AuditError('preceding Ring-profile boundary regressed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if tuple(fs)!=F or len(rows)!=17 or sum(r['source_path_anchor']=='yes' for r in rows)!=5 or sum(r['ghidra_discovered']=='yes' for r in rows)!=5:raise c.AuditError('function inventory changed')
 starts={a for a,_ in F};inter=set();ins={};calls=[];ind=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=d._recover_function(b,a,z)
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=2374 or sh(body)!='b472df1a76d28401bcb2b27b7157740d9de03f1373737056a0f5716e7be959f5' or code!=body or len(ins)!=861 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='8e28725f62906a8d89e2439de24baa6e2efc6f11cf68290bf080d5af17e08775' or ind:raise c.AuditError('instruction closure changed')
 if len(c._slice(b,*PHYS))!=2632 or sh(c._slice(b,*PHYS))!='6b8db1468e4f5c0d408f9e23ab2bb4cd8df324faa11cfef9c2db8102596be172' or len(c._slice(b,*POOL))!=258 or sh(c._slice(b,*POOL))!='8cfa93096f3b56bbe82f03fd2149308dde431d9c45584ef9c915ef4830956678':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='d79e7e2185ac4ff83650326fb3733dc1eae764aecd221fb0e93d71f9347cf393' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='bf5bdb786c42e0e88ba892177d2e17f9f782f7546f8730b3feb0fea4150b6c79':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS,IAR,HEAP,RING,EVENT,FIRST)
 if len(calls)!=171 or sum(y in starts for _,y in calls)!=9 or c._pair_digest(calls)!='396d475a0666f06abbef29bdbcb80ce9606918567fabff7e7cf7467c3e020f3a' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(110,10,2,2,3,13,16,6):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non=[];wide=[];wstrict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non.append((a,y))
  x,z=struct.unpack('<HH',c._slice(b,a,a+4));y=wide_branch_target(a,x,z)
  if y in starts:wide.append((a,y))
  elif y in inter:wstrict.append((a,y))
 if len(entries)!=21 or c._pair_digest(entries)!='d31fd6babf76415d5284a45608599c94dc1831a0e9ebd717147fec1f2a924a28' or strict or non or wide or wstrict:raise c.AuditError('branch ingress changed')
 stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0]
  if v&1 and (v&~1) in starts:stored.append((c.BASE+off,v&~1))
 if stored!=STORED or c._pair_digest(stored)!='83e64392ed3bdaaeedafe22a06e44aec0c5c5f2846411f95057b3c379afc1b35':raise c.AuditError('stored ingress changed')
 expected=r'D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ring.c'
 if cstr(b,PATH)!=expected or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=t.literal_references(b,CELL);owners=sum(any(a<=x<z for x in refs) for a,z in F)
 if len(refs)!=22 or owners!=9 or c._pair_digest([(CELL,x) for x in refs])!='df65a94afc841c402807831c04e805b98010b4c8013273cdc738ff5c8465711b':raise c.AuditError('path references changed')
 source=SOURCE.read_bytes()
 if len(source)!=18367 or sh(source)!=SOURCE_SHA:raise c.AuditError('production Ring thread source changed')
 source_text=source.decode('utf-8');required=('OPEN_CFW_THREAD_RING_QUEUE_DEPTH = 3u','OPEN_CFW_THREAD_RING_EVENT_MESSAGE = 0x400000u','record->length >= 2u','OPEN_CFW_THREAD_RING_EXIT_WAIT_FOREVER','open_cfw_thread_ring_record_send')
 if any(x not in source_text for x in required):raise c.AuditError('production Ring thread contract changed')
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')=='components/apollo_main/core_overlay/thread_ring.c']
 if tuple(x['function'] for x in leaves)!=SOURCE_FUNCTIONS or tuple(x['expected']['offset'] for x in leaves)!=SOURCE_OFFSETS or tuple(x['expected']['size'] for x in leaves)!=SOURCE_SIZES:raise c.AuditError('production Ring thread source placement changed')
 if sum(len(x['relocations']) for x in leaves)!=72 or any(x.get('profiles')!=['apple-clang'] or x.get('strict_relocation_contract') is not True or x.get('source',{}).get('sha256')!=SOURCE_SHA or x.get('source',{}).get('license')!='MIT' for x in leaves):raise c.AuditError('production Ring thread source authentication changed')
 patch_functions=PATCH_FUNCTIONS
 patches=[x for x in overlay['patch_sites'] if x.get('name','').startswith('replace_thread_ring_')]
 if len(patches)!=15 or tuple(x.get('target_function') for x in patches)!=patch_functions:raise c.AuditError('production Ring thread redirect inventory changed')
 patch_rows=[r for r in rows if int(r['stock_end_exclusive'],0)-int(r['stock_start'],0)>=4];span_by_name={function:(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for function,r in zip(PATCH_FUNCTIONS,patch_rows)}
 for i,patch in enumerate(patches,1):
  function=patch_functions[i-1];a,z=span_by_name[function]
  if patch.get('name')!=f'replace_thread_ring_{i:02d}' or patch.get('runtime_address')!=a or patch.get('expected_size')!=z-a or patch.get('expected_sha256')!=sh(c._slice(b,a,z)) or patch.get('branch')!='b_w' or patch.get('profiles')!=['apple-clang']:raise c.AuditError(f'production Ring thread redirect {i:02d} changed')
 report=json.loads(REPORT.read_text());built=[x for x in report['relocated_leaves'] if x.get('source',{}).get('path')=='components/apollo_main/core_overlay/thread_ring.c']
 validate_apollo_main_artifacts(ROOT,c.AuditError,'Ring thread')
 if len(built)!=17 or sum(x['placement']['size'] for x in built)!=894 or sum(x['placement']['padding_before'] for x in built)!=22:raise c.AuditError('production Ring thread build artifact changed')
 manifest=json.loads(SOURCE_MANIFEST.read_text());main=manifest['component_overrides']['apollo_main']
 regions=main['regions'];replacement=[x for x in regions if x['name'].startswith('thread_ring_') and x['name'].endswith('_source_replacement')];text_regions=[x for x in regions if x['name'].startswith('thread_ring_') and x['name'].endswith('_source_text')];alignment=[x for x in regions if x['name'].startswith('thread_ring_') and x['name'].endswith('_overlay_alignment')];retained=[x for x in regions if x['name'] in ('thread_ring_init_hook_retained_compatibility','thread_ring_resource_hook_retained_compatibility','thread_ring_retained_literal_pool')]
 if (len(replacement),sum(x['size'] for x in replacement),len(text_regions),sum(x['size'] for x in text_regions),len(alignment),sum(x['size'] for x in alignment),len(retained),sum(x['size'] for x in retained))!=(15,2370,17,894,11,22,3,262):raise c.AuditError('production Ring thread manifest ownership changed')
 return {'schema_version':1,'analysis_mode':'authenticated raw-image closure plus production source/artifact verification; no hardware operation','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\threads\thread_ring.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':17,'ghidra_discovered_functions':5,'restored_functions':12,'path_anchored_functions':5,'raw_path_references':22,'raw_path_referencing_functions':9,'body_bytes':2374,'physical_bytes':2632,'outer_pool_bytes':258,'reachable_instructions':861,'direct_body_calls':171,'internal_direct_body_calls':9,'external_direct_body_calls':162,'indirect_body_calls':0,'direct_bl_entry_sites':21,'stored_entry_pointers':8,'strict_interior_ingress':0},'behavior':{'cmsis_thread_lifecycle':True,'queue_record_dispatch':True,'ring_touch_pair_and_connection_policy':True,'delayed_event_scheduling':True,'bounded_callback_registration':True},'provider_boundary':{'easylogger_calls':110,'cmsis_freertos_calls':10,'freertos_assert_calls':2,'iar_dlib_calls':2,'source_owned_heap_wrapper_calls':3,'closed_ring_service_calls':13,'event_loop_calls':16,'other_first_party_calls':6,'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','tlsf_commit':'deff9ab509341f264addbd3c8ada533678591905','cmsis_wrappers':['osThreadNew','osThreadTerminate','osThreadFlagsSet','osThreadFlagsWait','osDelay','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet','osMessageQueueDelete'],'historical_thread_ring_commit':None,'new_version_discriminator':False,'private_generating_commit_recoverable':False},'production':{'candidate':str(SOURCE.relative_to(ROOT)),'source_inventory_available':True,'production_routed':True,'ownership_bytes':2370,'retained_compatibility_bytes':262,'compiled_text_bytes':894,'generated_alignment_bytes':22,'strict_relocations':72,'guarded_redirects':15,'hardware_validation':'blocked by unavailable physical evidence','hardware_blocker':'hardware validation is blocked by unavailable physical evidence; future qualification requires an authorized G2 pair and either a component-specific Ring transport fixture or an authenticated golden Ring transport capture'}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
