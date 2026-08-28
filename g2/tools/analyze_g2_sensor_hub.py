#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for sensor_hub.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-sensor-hub-function-map.tsv';PM=ROOT/'tools/manifests/g2-sensor-hub-provider-map.tsv';CL=ROOT/'tools/manifests/g2-sensor-hub-closure.tsv'
PINS={FM:'c2c4a76be4479a4439cee52987bb339a62ba838eed14af27a47961cdf300edbb',PM:'3b725828f8a539fb37aa2d05d835abade1dca4ebbb54ee4b537a67dfb3574827',CL:'3c161a89b559e77da739a50fb64856e8b964354f6272a62e5d0eb799bdd65e3b'}
PHYS=(0x4A6644,0x4A777C);PATH_ADDR=0x6FC974;CELLS=(0x4A6EDC,0x4A73E8)
SOURCE=ROOT/'components/apollo_main/core_overlay/sensor_hub.c';SOURCE_PATH='components/apollo_main/core_overlay/sensor_hub.c';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json';FLASH_PLAN=ROOT/'build/source/flash-plan.json'
SOURCE_PIN=(28473,'354ffec91cebe2a5121c6b2dbb66d7322f602285eba7da5e8f981c7de4b23748')
EASY={0x43CE9E,0x43D0CE,0x43D574}
LVGL={0x43DE82,0x43DFA4,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43FD9E,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x44131C,0x44140E,0x44143E,0x44145A,0x44146A,0x499416,0x49942E}
CLOSED_FP={0x4487AC,0x46C524,0x46D816,0x46D826,0x4A45B0,0x4A45BC,0x4A460C,0x4A499C,0x4A4E8C,0x4A4EC0,0x4A52A2,0x4A60E8,0x4A6270,0x4A6538,0x4A653E,0x4A6544,0x4A654A,0x4A6550,0x4A6556,0x4A655C,0x4A6568,0x4ABE60,0x4ADF74,0x4AE10A,0x4AE218,0x4C9B86,0x4C9BE2,0x5099F8}
CMSIS={0x4490CC,0x4490E2,0x4491FE,0x4493B0,0x449498,0x4494D8,0x449A32,0x449ABE,0x449B3C}
TR={0x45FFFE,0x460084};NANOPB={0x48949C};OPEN_FP={0x45A568}
STORED=[(0x686F7C,0x4A6AE9),(0x793AFC,0x4A6645),(0x793B00,0x4A683D)]
INTERIOR=[(0x456399,0x4A7201),(0x4563A3,0x4A7001),(0x46142D,0x4A76D5),(0x58F6E1,0x4A6FFB)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text());kernel=json.loads((ROOT/'third_party/freertos-kernel/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or cms['upstreams']['cmsis_5']['selected_commit']!='2b7495b8535bdcb306dac29b9ded4cfb679d7e5c' or kernel['upstream']['selected_commit']!='def7d2df2b0506d3d249334974f51e427c17a41c':raise c.AuditError('provider provenance changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=31 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort()
 if len(body)!=4026 or sh(body)!='f67ae887ce8c89b212e4988d5fbe82395a1499313ec1ca9d0b426e774e61ffa7' or len(ins)!=1465 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='36cea136498d43578291a39a9c7c439def0f9db3cd9e9d3e29acad6dab2e95a4' or ind!=[0x4A6916]:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=382 or sh(non)!='91187447eec05565cb1ee6afe6253a6c8eba6ceebf8118e876295b9956be522f' or sh(c._slice(b,*PHYS))!='5f83242db1a57ec291b26fabbb9426ab0ee9d85479c8d66cfb8b4806bdf0ea8e':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='1c668a83311886bd606fb6e87cb8599e3bee167e39cb9245178e0a0f575b2bd4' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='f71bf195c976a85e4b6685fc745586adffc0d52df99bfbfa137c2918f5ac90da':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,CLOSED_FP,CMSIS,TR,NANOPB,OPEN_FP)
 if len(calls)!=282 or sum(y in starts for x,y in calls)!=28 or c._pair_digest(calls)!='29b3b36bd201c69fe380d94b6ff86d101d397cc99da881acc24ca9f531350a49' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(130,69,36,9,8,1,1):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=61 or c._pair_digest(entries)!='4d9d233adaecbb09aa3da3dd4580b11ec3276d379235cd20949211b71a440a42' or strict or pseudo:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if stored!=STORED or interior!=INTERIOR or c._pair_digest(interior)!='7a3292ab600483e830be4912c5047c4cbb5962043e3c94a9084f466b903ab972':raise c.AuditError('stored ingress changed')
 o=PATH_ADDR-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0 or b[o:e].decode('ascii')!=r'D:\01_workspace\s200_ap510b_iar_git\platform\sensor_hub\sensor_hub.c':raise c.AuditError('path changed')
 refs=sorted((cell,x) for cell in CELLS for x in t.literal_references(b,cell))
 if len(refs)!=26 or c._pair_digest(refs)!='474e09ac914cb46707eb94f094a632ff9b04e27e91e29d5d3efeff7c6f00084b':raise c.AuditError('path refs changed')
 if (len(SOURCE.read_bytes()),sh(SOURCE.read_bytes()))!=SOURCE_PIN:raise c.AuditError('sensor-hub source changed')
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH];names={x['function'] for x in leaves}
 if len(leaves)!=31 or len(names)!=31 or not names<=set(overlay['functions']) or sum(x['expected']['size'] for x in leaves)!=1602 or sum(x['expected']['offset']-(leaves[i-1]['expected']['offset']+leaves[i-1]['expected']['size']) if i else x['expected']['offset']-313888 for i,x in enumerate(leaves))!=36 or sum(len(x['relocations']) for x in leaves)!=106:raise c.AuditError('sensor-hub production leaf closure changed')
 if any(x.get('profiles')!=['apple-clang'] or not x.get('strict_relocation_contract') or x.get('source',{}).get('license')!='GPL-3.0-only' for x in leaves):raise c.AuditError('sensor-hub production policy changed')
 patches=[x for x in overlay['patch_sites'] if x.get('target_function') in names]
 expected_patch={(int(r['stock_start'],0),int(r['stock_bytes']),r['stock_sha256']) for i,r in enumerate(rows,1) if i!=21}
 if len(patches)!=30 or sum(x['expected_size'] for x in patches)!=4024 or {(x['runtime_address'],x['expected_size'],x['expected_sha256']) for x in patches}!=expected_patch or any(x.get('branch')!='b_w' or x.get('profiles')!=['apple-clang'] for x in patches):raise c.AuditError('sensor-hub guarded replacement closure changed')
 build=json.loads(REPORT.read_text())
 validate_apollo_main_artifacts(ROOT,c.AuditError,'sensor hub')
 built=[x for x in build['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH]
 if len(built)!=31 or sum(x['placement']['size'] for x in built)!=1602 or sum(x['placement']['padding_before'] for x in built)!=36 or sum(x['extraction']['relocation_count'] for x in built)!=106:raise c.AuditError('sensor-hub built leaf closure changed')
 manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];sensor=[x for x in main['regions'] if x.get('name','').startswith('sensor_hub_')]
 if len(sensor)!=84 or sum(x['size'] for x in sensor if x.get('address_status')=='generated_source_entry_replacement')!=4024 or sum(x['size'] for x in sensor if x.get('address_status')=='official_blob')!=384 or sum(x['size'] for x in sensor if x.get('address_status')=='source_compiled')!=1602 or sum(x['size'] for x in sensor if x.get('address_status')=='generated_alignment')!=36:raise c.AuditError('sensor-hub manifest tiling changed')
 blocker='hardware testing is deferred by project direction; future physical qualification requires a responsive authorized G2 sensor path or golden IMU/ALS trace'
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\sensor_hub\sensor_hub.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':31,'ghidra_discovered_functions':5,'restored_functions':26,'path_anchored_functions':5,'body_bytes':4026,'physical_bytes':4408,'noncode_bytes':382,'reachable_instructions':1465,'direct_body_calls':282,'internal_direct_body_calls':28,'external_direct_body_calls':254,'indirect_body_calls':1,'direct_bl_entry_sites':61,'external_direct_bl_entry_sites':33,'stored_function_entry_pointers':3,'strict_interior_ingress':0,'raw_interior_word_collisions':4},'behavior':{'cmsis_thread_lifecycle':True,'queue_record_dispatch':True,'bounded_handler_table_dispatch':True,'imu_mode_and_calibration_policy':True,'calibration_display_feedback':True},'provider_boundary':{'easylogger_calls':130,'admitted_lvgl_calls':69,'closed_first_party_calls':36,'cmsis_freertos_calls':9,'translation_lookup_calls':8,'nanopb_calls':1,'bounded_open_first_party_calls':1,'freertos_kernel_direct_calls':0,'embedded_sensor_fusion_library':None,'cmsis_wrappers':['osKernelGetTickCount','osThreadNew','osThreadTerminate','osTimerNew','osTimerStart','osTimerStop','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet'],'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','new_version_discriminator':False},'production':{'source_inventory_available':True,'production_routed':True,'candidate':SOURCE_PATH,'source_functions':31,'compiled_text_bytes':1602,'generated_alignment_bytes':36,'guarded_redirects':30,'ownership_bytes':4024,'retained_compatibility_bytes':384,'strict_relocations':106,'hardware_validation':'deferred by project direction','hardware_blocker':blocker}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
