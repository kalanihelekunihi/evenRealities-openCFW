#!/usr/bin/env python3
"""Fail-closed object/provider audit for service_even_ai.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-service-even-ai-function-map.tsv';PM=ROOT/'tools/manifests/g2-service-even-ai-provider-map.tsv';CL=ROOT/'tools/manifests/g2-service-even-ai-closure.tsv'
PINS={FM:'6868fab715b9855ac6f37afe48b08f890959f02f8bedb6c22317b9a0aef624b5',PM:'a384dd68cbbb401ce2e397ce82b71bd2bb984229a39a96949fd0800f9c7fd413',CL:'8cd9188887d47921a4e9bcd98fa63ee8644be99d0c6b025b9e7cc8e7665aa5b7'}
F=((0x497DE6,0x497E08),(0x497E08,0x497EA2),(0x497EA2,0x498092),(0x498092,0x4982D4),(0x4982D4,0x4982F2),(0x4982F2,0x498310),(0x498310,0x49832E),(0x49832E,0x498528),(0x498528,0x4985A6))
PHYS=(0x497DE6,0x498634);POOL=(0x4985A6,0x498634);PATH=0x6EF8B8;CELL=0x4985B8
ANCHORS={0x497E08,0x49832E,0x498528}
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};CMSIS={0x4490CC}
CLOSED={0x4487AC,0x464F76,0x468034,0x469AE2,0x4ABE60,0x4E304C,0x4E3788,0x4E3B80,0x4E4CB8,0x4E5672,0x4E5D54}
BOUNDED={0x467F08,0x4E1FA6,0x4E1FBE}
STORED=[(0x49861C,0x497E09)];RAWCOL=[(0x4485D7,0x497FD5),(0x52AC03,0x4983B5),(0x64A583,0x497DFF)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstr(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or cms['upstreams']['cmsis_5']['selected_commit']!='2b7495b8535bdcb306dac29b9ded4cfb679d7e5c':raise c.AuditError('provider provenance changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if tuple(fs)!=F or len(rows)!=9 or sum(r['source_path_anchor']=='yes' for r in rows)!=3 or sum(r['ghidra_discovered']=='yes' for r in rows)!=6:raise c.AuditError('function inventory changed')
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  if set(ins)&set(ii):raise c.AuditError('overlap')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=1984 or sh(body)!='05a5b9ac7b913d5fbe4a6e004bca7891d685b1b4075fb3bab3b63421244b34c9' or code!=body or len(ins)!=753 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='b419c6eadfe775bbacf7486d749782ef66483a2872618c143a6c2d6856ce384f' or ind:raise c.AuditError('instruction closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=142 or sh(non)!='dc4f4e9180146f232baae967e4a4272bbe5b5f31458c3f244cc89067cc8be033' or non!=c._slice(b,*POOL) or sh(c._slice(b,*PHYS))!='6f45dddbc038fa5b95231512bc35ead4871d5e38b789cfff259cf40ba9083897':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='17c90599dfeeaf6aad8bbbf85eae6875468a80f47a0c794255b6b65573a190c9' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='a45175407df3e5d276a00b4e5bdaba75a46f19ef491a79c1a09d4d20cd10ddc6':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,CLOSED,BOUNDED)
 if len(calls)!=127 or sum(y in starts for x,y in calls)!=3 or c._pair_digest(calls)!='f681722a81afbdced9cc562b1d94a90417740cc6d09a912282e4f7d55107cfb1' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(55,9,2,23,35):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=30 or c._pair_digest(entries)!='92d6fa169508ee71602fdb2b9d2ac9f9ed07bf0c002f175de557658203483699' or strict or pseudo:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];rawcol=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored!=STORED or rawcol!=RAWCOL:raise c.AuditError('stored ingress changed')
 if cstr(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\platform\service\evenAI\service_even_ai.c' or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=t.literal_references(b,CELL)
 if len(refs)!=11 or sum(any(a<=x<z for x in refs) for a,z in F)!=4 or c._pair_digest([(CELL,x) for x in refs])!='e6772336e65be9676d76e4669839d31744dd5e33d01a4983c13f36cbf380ce64':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any(x.get('path','').lower().endswith('service_even_ai.c') for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\service\evenAI\service_even_ai.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':9,'ghidra_discovered_functions':6,'restored_functions':3,'path_anchored_functions':3,'raw_path_references':11,'body_bytes':1984,'physical_bytes':2126,'noncode_bytes':142,'reachable_instructions':753,'direct_body_calls':127,'internal_direct_body_calls':3,'external_direct_body_calls':124,'indirect_body_calls':0,'direct_bl_entry_sites':30,'stored_aligned_function_entry_pointers':1,'raw_interior_word_collisions':3,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':55,'iar_dlib_calls':9,'cmsis_freertos_calls':2,'closed_first_party_calls':23,'bounded_first_party_calls':35,'cmsis_freertos_seams':['osKernelGetTickCount'],'freertos_kernel_seams':[],'embedded_ai_nn_library':False,'ai_nn_negative_evidence':'all 124 external calls terminate at admitted EasyLogger IAR DLIB CMSIS-FreeRTOS tick or bounded first-party providers; no NN kernel DSP or inference provider edge exists','cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','historical_service_even_ai_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
