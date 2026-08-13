#!/usr/bin/env python3
"""Fail-closed stock/provider audit for ring_connect_policy.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_dashboard_watchface_manager as d
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ring-connect-policy-function-map.tsv';PM=ROOT/'tools/manifests/g2-ring-connect-policy-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ring-connect-policy-closure.tsv'
PINS={FM:'d368e986ca1a14b17e9c86d731d3711c9f70b5c5634483699294696cac6a64e9',PM:'2ffd806820e42a16158ccc6c1638dfeedd8793cd7cb9d4e709a6fd5138e36a31',CL:'bb3df90db3c9ab6a3384cf4a7aaa18ae699a11bae197dd1bcbfffab2ae12cb9b'}
F=((0x49F020,0x49F028),(0x49F028,0x49F040),(0x49F040,0x49F05C),(0x49F05C,0x49F0DA),(0x49F0DA,0x49F15A),(0x49F15A,0x49F326),(0x49F326,0x49F438),(0x49F438,0x49F4A8),(0x49F4A8,0x49F500),(0x49F500,0x49F552),(0x49F552,0x49F5F8),(0x49F5F8,0x49F646),(0x49F646,0x49F6AE),(0x49F6AE,0x49F702),(0x49F702,0x49F744))
PHYS=(0x49F020,0x49F828);POOL=(0x49F744,0x49F828);PREV_POOL=(0x49EFAC,0x49F020);NEXT=(0x49F828,0x49F870);PATH=0x6E15FC;CELL=0x49F750
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490CC};EVENT={0x47697E,0x476ACE};PAIR={0x4BC418};CENTRAL={0x4A2914}
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
 if tuple(fs)!=F or len(rows)!=15 or sum(r['source_path_anchor']=='yes' for r in rows)!=12 or sum(r['ghidra_discovered']=='yes' for r in rows)!=11:raise c.AuditError('function inventory changed')
 starts={a for a,_ in F};inter=set();ins={};calls=[];ind=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=d._recover_function(b,a,z)
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=1828 or sh(body)!='287e96848aaeedaab508524bd67f47a9bb05ce264eef9a028965044f3b7f27a6' or code!=body or len(ins)!=702 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='0a5d3fece9ce50815bee04dae14466b372843940b73ff544315916a7364e3cf9' or ind:raise c.AuditError('instruction closure changed')
 if len(c._slice(b,*POOL))!=228 or sh(c._slice(b,*POOL))!='7d15d4ff35e78076d0263615ea3d19309ed6e836801140133c2ff09cc5219faa' or len(c._slice(b,*PHYS))!=2056 or sh(c._slice(b,*PHYS))!='d17d16c61d0a3df734d7945192bc93f734a368d78a0afd820c7d2800a7a74483':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,*PREV_POOL))!='9659fd8a4bd5654bc4fa5e9c529c069749130809f26637c2a51f25ebc269954d' or sh(c._slice(b,*NEXT))!='2bc8b61c1ebc5dfd74cbe6341579879f63bcb7879ab732f1651e7275dfd0bf08':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,EVENT,PAIR,CENTRAL)
 if len(calls)!=120 or sum(y in starts for _,y in calls)!=12 or c._pair_digest(calls)!='430756429ddb1378bf125caf6272e456df832a7f3ae9174abd89d18f7290029b' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(95,1,10,1,1):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non.append((a,y))
 if len(entries)!=29 or c._pair_digest(entries)!='271f044ed708729f9757d5f6eb6d2372358361564028d25baced45c83eac4c16' or strict or non:raise c.AuditError('BL ingress changed')
 stored=[];raw=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];y=v&~1
  if y in starts or y in inter:raw.append((c.BASE+off,v,y))
  if v&1 and y in starts:stored.append((c.BASE+off,y))
 if stored!=[(0x49F7EC,0x49F500)] or raw!=[(0x49F7EC,0x49F501,0x49F500),(0x4F468A,0x49F640,0x49F640)]:raise c.AuditError('raw pointer topology changed')
 if cstr(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\platform\protocols\ring_service\ring_connect_policy.c' or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=t.literal_references(b,CELL)
 if len(refs)!=19 or sum(any(a<=x<z for x in refs) for a,z in F)!=12 or c._pair_digest([(CELL,x) for x in refs])!='b6b61d32b514f7fa8ae8fcfda81359dbc60da5aab0941d51b0b4adbe6bb053c3':raise c.AuditError('path references changed')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\protocols\ring_service\ring_connect_policy.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':15,'ghidra_discovered_functions':11,'restored_functions':4,'path_anchored_functions':12,'raw_path_references':19,'raw_path_referencing_functions':12,'body_bytes':1828,'physical_bytes':2056,'noncode_bytes':228,'reachable_instructions':702,'direct_body_calls':120,'internal_direct_body_calls':12,'external_direct_body_calls':108,'indirect_body_calls':0,'direct_bl_entry_sites':29,'stored_entry_pointers':1,'raw_interior_word_collisions':1,'strict_interior_ingress':0},'behavior':{'dominant_hand_switch_window':True,'connect_info_throttle':True,'connect_timeout_scheduling':True,'reconnect_failure_notification':True,'connect_success_scheduling':True,'policy_reset_variants':2},'provider_boundary':{'easylogger_calls':95,'cmsis_freertos_calls':1,'closed_event_loop_calls':10,'closed_nanopb_facade_calls':1,'closed_ble_central_calls':1,'direct_cordio_calls':0,'direct_nanopb_calls':0,'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','historical_ring_connect_policy_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
