#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for health/ui_health_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as th
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ui-health-page-function-map.tsv';PM=ROOT/'tools/manifests/g2-ui-health-page-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ui-health-page-closure.tsv'
SOURCE=ROOT/'components/apollo_main/core_overlay/ui_health_page.c';SOURCE_PATH='components/apollo_main/core_overlay/ui_health_page.c';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';REPORT=ROOT/'components/apollo_main/core_overlay/build/build-report.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json';FLASH_PLAN=ROOT/'build/source/flash-plan.json'
SOURCE_PIN=(35724,'b28e90c235b3fde96ad19413cd84a328df770f1d60d329994e0dfcf09024c049')
ARTIFACT_PINS=(332148,'588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d',3855544,'df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc',4634038,'3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731')
PINS={FM:'0adbacae43bd638de1ba2ddcac25a7758135d298591d7e46e26288ccb3bafe0b',PM:'966d24d2abf45d0df9263751c3f5656793dc7b3f1d1d98e1b83173ad9792ac08',CL:'f4d4281023bc1f4ec2e7b70d1055cc930512f2737bb7b36164626bcc108e5b2a'}
PHYS=(0x4FB1FA,0x4FD940);PATH=0x707B9C;CELLS=(0x4FB708,0x4FC608,0x4FD924)
EASY={0x43CE9E,0x43D0CE,0x43D574};RUNTIME={0x43C0E4};MPALAND={0x4B4728}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6B8,0x43F6D6,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44133A,0x441378,0x441386,0x441394,0x4413A2,0x4413B0,0x44140E,0x44142E,0x44143E,0x44145A,0x44146A,0x44D7B8,0x44D878,0x44DCE2,0x44DDEA,0x44E368,0x44E3CA,0x44E498,0x44EA04,0x4503D6,0x450408,0x4506CE,0x498668,0x498680,0x499416,0x49942E}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(fs)!=12 or sum(r['path_anchored']=='yes' for r in rows)!=7 or sum(r['ghidra_discovered']=='yes' for r in rows)!=11:raise c.AuditError('function inventory changed')
 starts={a for a,_ in fs};ins={};calls=[];dyn=[];body=b'';un=[]
 for a,z in fs:
  ii,cc,dd=cfg._recover_function(b,a,z);ins.update(ii);calls+=cc;dyn+=dd;body+=c._slice(b,a,z);un+=c._uncovered((a,z),ii)
 calls.sort();gaps=[(0x4FB5E6,0x4FB5E8),(0x4FBA2E,0x4FBA34),(0x4FBC8C,0x4FBC94),(0x4FBE06,0x4FBE10),(0x4FC902,0x4FC908),(0x4FCBB0,0x4FCBB8),(0x4FCD8C,0x4FCD94),(0x4FCFD2,0x4FCFD8),(0x4FD1EC,0x4FD1F0),(0x4FD450,0x4FD45C),(0x4FD5B0,0x4FD5D0),(0x4FD6B6,0x4FD6C4)]
 if un!=gaps or len(body)!=9414 or sh(body)!='2e96d8bf1f49a043972dfe971e9395e83480288162fa887dc5d984ea8970cea0' or len(ins)!=3235 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='fb9114efc3198bcb733ad0c4035807af5b08a65d412758ed60440e81defca627' or dyn:raise c.AuditError('body closure changed')
 cov=set()
 for a,i in ins.items():cov.update(range(a,a+i.size))
 outer=bytes(v for a,v in zip(range(*PHYS),c._slice(b,*PHYS)) if a not in cov)
 if len(outer)!=756 or sh(outer)!='c16b47740f1401ec1af0499c3d330af9e73b77028e1c1027b96817b0af831d71' or sh(c._slice(b,*PHYS))!='a34d3c62aca5ba791be93376c0a59c94ce8117c25e6ae5bcc55ac1f934f0159a':raise c.AuditError('physical closure changed')
 ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-RUNTIME-MPALAND
 if len(calls)!=678 or sum(t in starts for _,t in calls)!=12 or c._pair_digest(calls)!='1c2571ab02aeccd46342d04e2615c5b7909938c8953eab8393ffaa36d4295d84' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,RUNTIME,MPALAND,first))!=(437,55,4,36,134):raise c.AuditError('provider closure changed')
 interiors=set(ins)-starts;entries=[];strict=[];non=[];wide=[];ws=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  t=th._thumb_bl_target(b,a)
  if t in starts:entries.append((a,t))
  elif t in interiors:strict.append((a,t))
  elif t is not None and PHYS[0]<=t<PHYS[1]:non.append((a,t))
  x,y=struct.unpack('<HH',c._slice(b,a,a+4));t=wide_branch_target(a,x,y)
  if t in starts:wide.append((a,t))
  elif t in interiors:ws.append((a,t))
 if len(entries)!=19 or c._pair_digest(entries)!='cb0dce70b026105e22af13131a8931a4e914df8b98f000874723bda5c5aee1e6' or strict or non!=[(0x4FE37E,0x4FD93C)] or wide or ws:raise c.AuditError('branch classification changed')
 raw=[];stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];t=v&~1
  if t in starts or t in interiors:
   raw.append((c.BASE+off,v,t))
   if t in starts and (c.BASE+off)%4==0 and v&1:stored.append((c.BASE+off,v))
 if len(raw)!=5 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='429b30c81ddd74f8307f35ea83d3c115ecbf86284af4f2f05f27fe815a52b69c' or len(stored)!=2 or c._pair_digest(stored)!='fc3bf006b5a36d465d6149f9b9e3bf4a2f43e107e297b3d6cef92b6afadf4dc0':raise c.AuditError('stored ingress changed')
 o=PATH-c.BASE;e=b.find(b'\0',o)
 if b[o:e].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\health\ui_health_page.c':raise c.AuditError('path changed')
 refs=sorted((cell,a) for cell in CELLS for a in th.literal_references(b,cell))
 if len(refs)!=11 or c._pair_digest(refs)!='08a14adbabcd995d33fd0d36b51df2761692ebdece7448857f5425ebb18c7222':raise c.AuditError('path refs changed')
 if (len(SOURCE.read_bytes()),sh(SOURCE.read_bytes()))!=SOURCE_PIN:raise c.AuditError('health-page source changed')
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH];names={x['function'] for x in leaves}
 if len(leaves)!=12 or len(names)!=12 or not names<=set(overlay['functions']) or sum(x['expected']['size'] for x in leaves)!=3978 or sum(x['expected'].get('closure_size',x['expected']['size']) for x in leaves)!=4306 or sum(len(x['relocations']) for x in leaves)!=269:raise c.AuditError('health-page production leaf closure changed')
 padding=sum(x['expected']['offset']-(leaves[i-1]['expected']['offset']+leaves[i-1]['expected'].get('closure_size',leaves[i-1]['expected']['size'])) if i else x['expected']['offset']-326460 for i,x in enumerate(leaves))
 if padding!=10 or any(x.get('profiles')!=['apple-clang'] or not x.get('strict_relocation_contract') or x.get('source',{}).get('license')!='GPL-3.0-only' for x in leaves):raise c.AuditError('health-page production policy changed')
 patches=[x for x in overlay['patch_sites'] if x.get('target_function') in names];expected_patch={(a,z-a,sh(c._slice(b,a,z))) for a,z in fs}
 if len(patches)!=12 or sum(x['expected_size'] for x in patches)!=9414 or {(x['runtime_address'],x['expected_size'],x['expected_sha256']) for x in patches}!=expected_patch or any(x.get('branch')!='b_w' or x.get('profiles')!=['apple-clang'] for x in patches):raise c.AuditError('health-page guarded replacement closure changed')
 build=json.loads(REPORT.read_text());pins=(build['overlay']['size'],build['overlay']['sha256'],build['component']['size'],build['component']['sha256'])
 if pins!=ARTIFACT_PINS[:4]:raise c.AuditError('health-page canonical component changed')
 built=[x for x in build['relocated_leaves'] if x.get('source',{}).get('path')==SOURCE_PATH]
 if len(built)!=12 or sum(x['extraction']['size'] for x in built)!=3978 or sum(x['placement']['size'] for x in built)!=4306 or sum(x['placement']['padding_before'] for x in built)!=10 or sum(x['extraction']['relocation_count'] for x in built)!=269:raise c.AuditError('health-page built leaf closure changed')
 manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions=[x for x in main['regions'] if x.get('name','').startswith('ui_health_page_')];tail=[x for x in main['regions'] if x.get('name')=='opaque_after_ui_health_page_before_ring_battery_service']
 counts={key:sum(x['size'] for x in regions if x.get('address_status')==key) for key in ('generated_source_entry_replacement','official_blob','source_compiled','generated_alignment')}
 if len(regions)!=37 or len(tail)!=1 or (tail[0]['target_address'],tail[0]['size'])!=(0x4FD870,8308) or counts!={'generated_source_entry_replacement':9414,'official_blob':432,'source_compiled':4306,'generated_alignment':10}:raise c.AuditError('health-page manifest tiling changed')
 if (main['provider']['size'],main['provider']['sha256'],manifest['package']['expected_size'],manifest['package']['expected_sha256'])!=ARTIFACT_PINS[2:]:raise c.AuditError('health-page package identity changed')
 plan_bytes=FLASH_PLAN.read_bytes();plan=json.loads(plan_bytes)
 if (len(plan_bytes),sh(plan_bytes))!=(3108201,'e91992690cb5766623f0b95b0928d3113ea9c0deac6d12275d55db6f12741297') or plan.get('package_sha256')!=ARTIFACT_PINS[5] or tuple(len(plan[key]) for key in ('flash_regions','unresolved_flash_regions','container_only_regions','protected_regions'))!=(4482,2,5,6):raise c.AuditError('health-page deployment plan changed')
 blocker='authorized right temple is nonresponsive; authorized left temple must remain stock; no responsive authorized G2 pair or golden health-page UI trace is available'
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\health\ui_health_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':12,'ghidra_discovered_functions':11,'path_anchored_functions':7,'restored_non_anchor_functions':1,'body_bytes':9414,'physical_bytes':10054,'outer_pool_bytes':756,'reachable_instructions':3235,'direct_body_calls':678,'internal_direct_body_calls':12,'external_direct_body_calls':666,'indirect_body_calls':0,'direct_bl_entry_sites':19,'stored_function_pointers':2,'classified_noncode_pseudo_bl_sites':1},'provider_boundary':{'lvgl_calls':437,'easylogger_calls':55,'cmsis_freertos_calls':0,'runtime_calls':4,'mpaland_printf_calls':36,'first_party_calls':134,'historical_health_page_commit':None,'new_version_discriminator':False},'behavior':{'two_page_health_view':True,'health_metric_formatting':True,'goal_progress_scaling':True,'deferred_fifo_events':True,'animated_page_switching':True,'refresh_and_teardown':True},'production':{'source_inventory_available':True,'production_routed':True,'candidate':SOURCE_PATH,'source_functions':12,'compiled_text_bytes':3978,'compiled_rodata_bytes':328,'generated_alignment_bytes':10,'guarded_redirects':12,'ownership_bytes':9414,'retained_compatibility_bytes':640,'strict_relocations':269,'hardware_validation':'blocked_unavailable_physical_evidence','hardware_blocker':blocker}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
