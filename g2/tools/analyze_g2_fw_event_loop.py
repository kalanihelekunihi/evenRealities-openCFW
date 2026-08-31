#!/usr/bin/env python3
"""Fail-closed stock/provider/source-route audit for fw_event_loop.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_dashboard_watchface_manager as d
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-fw-event-loop-function-map.tsv';PM=ROOT/'tools/manifests/g2-fw-event-loop-provider-map.tsv';CL=ROOT/'tools/manifests/g2-fw-event-loop-closure.tsv'
PINS={FM:'6c2c1fb4798f772c8e3856025a821d4ecd12c2f83f1e72ac6c99f3da6d56e329',PM:'ea73ad54b596a15fe71a137912af575cec17d48539e647b5f1c57cbe8f92e800',CL:'6dad564cf39607f90e24873e7566fff9fffbedb94d01b61cb182fb304984bb48'}
F=((0x4764E0,0x47667E),(0x476680,0x4766EC),(0x4766EC,0x4767A8),(0x4767A8,0x47697E),(0x47697E,0x476ACE),(0x476ACE,0x476BF0));PHYS=(0x4764E0,0x476CBC);POOL=(0x476BF0,0x476CBC);PATH=0x6F3C38;CELL=0x476C00
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490CC,0x4490E2,0x4491FE,0x449376,0x4493B0,0x449498,0x4494D8,0x44971C,0x4497B6,0x44981C,0x449A32,0x449ABE,0x449B3C};FREERTOS={0x4420D0,0x4420E8}
ROUTES={0x4764E0:'open_cfw_event_loop_initialize',0x476680:'open_cfw_event_loop_task',0x4766EC:'open_cfw_event_loop_push',0x4767A8:'open_cfw_event_loop_timer_callback',0x47697E:'open_cfw_event_loop_push_delayed',0x476ACE:'open_cfw_event_loop_remove_delayed'}
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
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or cms['upstreams']['cmsis_5']['selected_commit']!='2b7495b8535bdcb306dac29b9ded4cfb679d7e5c' or kernel['upstream']['selected_commit']!='def7d2df2b0506d3d249334974f51e427c17a41c':raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if tuple(fs)!=F or len(rows)!=6 or sum(r['source_path_anchor']=='yes' for r in rows)!=5 or sum(r['ghidra_discovered']=='yes' for r in rows)!=5:raise c.AuditError('function inventory changed')
 starts={a for a,_ in F};inter=set();ins={};calls=[];ind=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=d._recover_function(b,a,z)
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=1806 or sh(body)!='5737c580b89b68aa67efc2663029f956ad064faadd9ab4bee6886176f42fd087' or code!=body or len(ins)!=661 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='b3285f5029774c3cbdce331e5c3b2edb7247ba5b699aab00d264a3a6be026a01' or ind!=[0x47668A]:raise c.AuditError('instruction closure changed')
 if c._slice(b,0x47667E,0x476680)!=b'\0\0' or len(c._slice(b,*POOL))!=204 or sh(c._slice(b,*POOL))!='d4be69e09c378bb4984fc56b42a3222bec9331fc25602fdcf8012a0ffb1babe5' or len(c._slice(b,*PHYS))!=2012 or sh(c._slice(b,*PHYS))!='0bbcc801083fbb26cfc647b82baec5f80c099e555ab8e17a6b1370695f88dd5f':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='724b9672998f2f9c356f5e8d76e469be48e4ec2a6c3f9766dfef5c86b853e8c9' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='b4e0d8adc612767dcfac91409991dce463bf361274171743c8e34eaac4346337':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS)
 if len(calls)!=108 or sum(y in starts for _,y in calls)!=4 or c._pair_digest(calls)!='4e2c6ed35e27627fbc7bdc995e88f3b84f70d1f214c855ab91970595cf3087af' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(80,20,4):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non.append((a,y))
 if len(entries)!=198 or c._pair_digest(entries)!='a1febb941c19ba0ac529e4307b3088cdee2d76642a127b5174e157d15a78022a' or strict or non:raise c.AuditError('BL ingress changed')
 stored=[];raw=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];y=v&~1
  if y in starts or y in inter:raw.append((c.BASE+off,v,y))
  if v&1 and y in starts:stored.append((c.BASE+off,y))
 if stored or raw!=[(0x64CE7B,0x476AFF,0x476AFE)]:raise c.AuditError('raw pointer topology changed')
 if cstr(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\framework\fw_event_loop\fw_event_loop.c' or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=t.literal_references(b,CELL)
 if len(refs)!=16 or sum(any(a<=x<z for x in refs) for a,z in F)!=6 or c._pair_digest([(CELL,x) for x in refs])!='f89b3ab1843be015f7e678b295a2d298f6d3c6c8d8376f7425401084fb11a2bb':raise c.AuditError('path references changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());source=next((x for x in overlay['sources'] if x.get('path')=='components/apollo_main/core_overlay/event_loop.c'),None)
 if source is None or source.get('sha256')!='768f13c0159628012fe292b0b34944a939b64d0c83dbc60ea24a02a4510ea119' or sh((ROOT/source['path']).read_bytes())!=source['sha256']:raise c.AuditError('production source route changed')
 routes={x['runtime_address']:x['target_function'] for x in overlay['patch_sites'] if x.get('runtime_address') in ROUTES}
 if routes!=ROUTES:raise c.AuditError('production replacement set changed')
 return {'schema_version':1,'analysis_mode':'read-only raw-image and production-route closure','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'framework\fw_event_loop\fw_event_loop.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':6,'ghidra_discovered_functions':5,'restored_functions':1,'path_anchored_functions':5,'raw_path_references':16,'raw_path_referencing_functions':6,'body_bytes':1806,'physical_bytes':2012,'noncode_bytes':206,'reachable_instructions':661,'direct_body_calls':108,'internal_direct_body_calls':4,'external_direct_body_calls':104,'indirect_body_calls':1,'bounded_indirect_body_calls':1,'direct_bl_entry_sites':198,'stored_entry_pointers':0,'raw_interior_word_collisions':1,'strict_interior_ingress':0},'behavior':{'cmsis_resource_initialization':True,'immediate_callback_queue':True,'bounded_delayed_callback_slots':64,'one_shot_timer_rescheduling':True,'callback_remove_by_function_and_argument':True},'provider_boundary':{'easylogger_calls':80,'cmsis_freertos_calls':20,'freertos_critical_port_calls':4,'bounded_first_party_indirect_calls':1,'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','historical_fw_event_loop_commit':None,'new_version_discriminator':False},'production':{'production_routed':True,'source_routed_functions':6,'source_sha256':source['sha256']}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
