#!/usr/bin/env python3
"""Fail-closed object/provider audit for platform/service/box_detect/service_box_detect.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-service-box-detect-function-map.tsv';PM=ROOT/'tools/manifests/g2-service-box-detect-provider-map.tsv';CL=ROOT/'tools/manifests/g2-service-box-detect-closure.tsv'
PINS={FM:'c21249e8c9dc024cbd2e7a1ae0ca0d19d811614f8a2a2e918a8a43f9365d1649',PM:'645b777fc23ccdccc2fc7757751098948419734f645ae4714f772afadae944eb',CL:'d231641492a65fee94ded1757299e893067fd83cd548d90e56dd08cf3326f235'}
PHYS=(0x4ABEC8,0x4ACE10);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};CMSIS={0x4493B0,0x449498,0x4494D8,0x449522,0x44953E};FIRST={0x443484,0x4487AC,0x45A568,0x464F76,0x465480,0x46B0EC,0x47243A,0x474100,0x47432C,0x4A2658,0x4A316C,0x4ABE60,0x4C659A,0x50938E,0x510A0C,0x510DEC,0x510FE2,0x5130A6}
CALLBACKS=((0x4AC016,0x4AC020),(0x4AC020,0x4AC02A))
STORED=[(0x4ACAA8,0x4AC017),(0x4ACB10,0x4AC021),(0x6A4614,0x4ACB41),(0x7490D8,0x4AC279)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53':raise c.AuditError('CMSIS-FreeRTOS changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 mapped=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 F=sorted(mapped+list(CALLBACKS));starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(mapped)!=32 or len(F)!=34 or sum(r['source_path_anchor']=='yes' for r in rows)!=9:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,mapped):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
 for a,z in F:
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=3584 or sh(body)!='68100f39a237057c199fc2203136da38ce4350c2d7a892ae6fb4f3bbd2b53942' or len(ins)!=1336 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='675153b07f749ff90bb6095bfd72df2fc295d78aa0caf3a3b7009fc7042cacd3' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=328 or sh(non)!='d416a454eb81917f4da732946ed3d6456b6798896741cf14d1df79349f0e91f7' or sh(c._slice(b,*PHYS))!='1b91af03dcd3f55f566d12c8fffc0ab1e4656eca0a502814d7011abfe3ea50dd':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='f1e4c80ba48c6d743b5733e81abe29db26313b7b8875382f8fdad026469b5f73' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='493e142f91934a58dd8648f0d86b2edf1b1d1ccf9ba04750f33132a31b67cf3a':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,FIRST)
 if len(calls)!=211 or sum(y in starts for x,y in calls)!=39 or c._pair_digest(calls)!='d6cc1ef7ceebef8bfdf84ce9e91cda911ed754f162b020239b8b9f84f569e3d0' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(130,7,13,22):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=65 or c._pair_digest(entries)!='ebc70a480a6f657ca20fa3c84be1e5809cb6dcd8733a24777229985e730f760e' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored!=STORED or c._pair_digest(stored)!='2c449e46de2bd2d1ad6885a3c1d6d425fda5a407d7c8f515f1f26d5c1e97502c' or interior:raise c.AuditError('stored ingress changed')
 pairs=[]
 for cell in (0x4AC818,0x4ACDBC):pairs+=[(cell,x) for x in t.literal_references(b,cell)]
 if len(pairs)!=26 or c._pair_digest(pairs)!='85df177b075a1064c2cb049a496ab4ac9f39158b1655f5785c831594f8e4453c':raise c.AuditError('path refs changed')
 off=0x6E4B68-c.BASE
 if b[off:b.find(b'\0',off)].decode()!=r'D:\01_workspace\s200_ap510b_iar_git\platform\service\box_detect\service_box_detect.c':raise c.AuditError('retained path changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 source=ROOT/'components/apollo_main/core_overlay/service_box_detect.c';source_sha=sh(source.read_bytes())
 leaves=[x for x in overlay['relocated_leaves'] if x.get('source',{}).get('path','').endswith('service_box_detect.c')]
 names={x['function'] for x in leaves};routes=[x for x in overlay['patch_sites'] if x.get('target_function') in names]
 if len(leaves)!=34 or len(names)!=34 or len(routes)!=34 or sum(x['expected']['size'] for x in leaves)!=1626 or sum(len(x['relocations']) for x in leaves)!=77:raise c.AuditError('box-detect production inventory changed')
 if any(not x.get('strict_relocation_contract') or x['source'].get('sha256')!=source_sha for x in leaves):raise c.AuditError('box-detect source/relocation contract changed')
 expected_routes={(a,z-a) for a,z in F};observed_routes={(x['runtime_address'],x['expected_size']) for x in routes}
 if observed_routes!=expected_routes:raise c.AuditError('box-detect routing changed')
 if overlay['expected']!={'overlay_size':426394,'overlay_sha256':'4b39c8a836154fada2b452be5f7de25c76541ed3d3cc8685571ff5d73cbfd999','component_size':3949790,'component_sha256':'0548bcfe565e675ee2883961bdead6e6441b593fca755278b637ffd908e0b32c'}:raise c.AuditError('box-detect aggregate pins changed')
 return {'schema_version':2,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\service\box_detect\service_box_detect.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':34,'ghidra_discovered_functions':3,'restored_functions':31,'path_anchored_functions':9,'body_bytes':3584,'physical_bytes':3912,'noncode_bytes':328,'reachable_instructions':1336,'direct_body_calls':211,'internal_direct_body_calls':39,'external_direct_body_calls':172,'indirect_body_calls':0,'direct_bl_entry_sites':65,'stored_function_entry_pointers':4,'raw_instruction_word_interior_collisions':0,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':130,'iar_dlib_calls':7,'cmsis_freertos_calls':13,'cmsis_freertos_seams':{'osTimerNew':2,'osTimerStart':2,'osTimerStop':6,'osTimerIsRunning':1,'osTimerDelete':2},'first_party_calls':22,'historical_box_detect_commit':None,'new_version_discriminator':False},'production':{'production_routed':True,'source_functions':34,'compiled_text_bytes':1626,'alignment_bytes':36,'strict_relocations':77,'replaced_stock_body_bytes':3584,'hardware_validation':'blocked_unavailable_authorized_physical_evidence'}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
