#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for thread_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-thread-manager-function-map.tsv';PM=ROOT/'tools/manifests/g2-thread-manager-provider-map.tsv';CL=ROOT/'tools/manifests/g2-thread-manager-closure.tsv'
PINS={FM:'2b21d0cfd40dffb9130825e29bfda7b9d202c6a9484bfa16b173d0a08f5b6455',PM:'3b99d6242c2249d51402dd9b1c3a623535fccf878c895be067b59e703b013c7d',CL:'1d304857f324a3b802e93a40eec193e1efbeaafeca87384fd91cab7cc79f56a1'}
PHYS=(0x4C94C8,0x4C9D44);PATH=0x6FE42C;CELL=0x4C9CA0
EASY={0x43CE9E,0x43D0C8,0x43D0CE,0x43D574,0x448E48};CMSIS={0x44903C,0x449094,0x4490CC,0x4490E2,0x4491AA,0x4491B2,0x4491FE,0x449238,0x4492C2,0x449590,0x4495E4,0x44969C};FREERTOS={0x5FA0A4};LFS={0x47627E};CLOSED={0x43C7CC,0x46FE38,0x4764E0,0x47697E,0x4ABE60,0x4B892C,0x541240,0x541302,0x541A2E};FIRST={0x47E232,0x54171C}
STORED=[(0x4C9D24,0x4C98C2),(0x4C9D28,0x4C9B1A),(0x79410C,0x4C9B48)];RAW=[(0x541825,0x4C9986)];IND=[0x4C9566,0x4C956E,0x4C9576,0x4C957E,0x4C9586,0x4C958E,0x4C9596,0x4C959E,0x4C95A6,0x4C95AE]
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
 if 'physical_interval\t[0x004C9D44,0x004CA6F8)' not in (ROOT/'tools/manifests/g2-uled-manager-closure.tsv').read_text():raise c.AuditError('following uLED-driver boundary regressed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=17 or sum(r['source_path_anchor']=='yes' for r in rows)!=6 or sum(r['ghidra_discovered']=='yes' for r in rows)!=15:raise c.AuditError('function inventory changed')
 starts={a for a,_ in F};inter=set();ins={};calls=[];ind=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=1934 or sh(body)!='c05a246c6814e3ff661b96166c7907934c9b102dcea861e861716fdc2e2169e5' or code!=body or len(ins)!=686 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='d81ec0ef19970528d0831ba2cdd852509717b8ae195b30ada1f4f59a214015ac' or ind!=IND:raise c.AuditError('instruction closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=238 or sh(non)!='446f955f9eaef8b8c58fd0547efcdd052ea585253652e26754bbd42df60043cd' or sh(c._slice(b,*PHYS))!='72e5943246e662a05a8258874c381f906c2a5cc4d1c659883fb9476c7b5300c8':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='a287dac854b47c81432fe66ba57ee7b4f711264982aaf3d1b934b3c81d7d9d8f' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='400f1c17e40fd69bd42b5eb30be98bac95a8e552ac9929b2039cdfd727ec9a87':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS,LFS,CLOSED,FIRST)
 if len(calls)!=140 or sum(y in starts for _,y in calls)!=23 or c._pair_digest(calls)!='a40487fd8a487bf26b537154c2061a2a46da799fe91c187a1fb55f397df75912' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(72,30,3,1,9,2):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non=[];wide=[];wstrict=[];inter_i=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter_i:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non.append((a,y))
  x,z=struct.unpack('<HH',c._slice(b,a,a+4));y=wide_branch_target(a,x,z)
  if y in starts:wide.append((a,y))
  elif y in inter_i:wstrict.append((a,y))
 if len(entries)!=680 or c._pair_digest(entries)!='c5d5523ae9927b9cddd6e16bb9fc02626dfc30652dfe98b64a010230863d8a6e' or strict or non or wide or wstrict:raise c.AuditError('branch ingress changed')
 stored=[];raw=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0]
  if v&1 and (v&~1) in starts:stored.append((c.BASE+off,v&~1))
  elif v&1 and (v&~1) in inter_i:raw.append((c.BASE+off,v&~1))
 if stored!=STORED or c._pair_digest(stored)!='d7ab0ea52847058d515ba2dbe3931bc4020ced21f467c8b907f772af0c056a94' or raw!=RAW or c._pair_digest(raw)!='d8c50a375a946661b8e7bfb0c9cbf331cc3a7e1ad67869d4e32e3e1ff7ccce13':raise c.AuditError('stored ingress changed')
 expected=r'D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_manager.c'
 if cstr(b,PATH)!=expected or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=[(CELL,x) for x in t.literal_references(b,CELL)]
 if len(refs)!=14 or c._pair_digest(refs)!='80941b28b50ff33367888dbf09fd778f620df66368e7346f7d018f0fe5e5e775':raise c.AuditError('path references changed')
 routed=any('thread_manager' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 if routed:raise c.AuditError('unimplemented thread manager entered production overlay')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure; corpus-independent','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\threads\thread_manager.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':17,'ghidra_discovered_functions':15,'restored_functions':2,'path_anchored_functions':6,'raw_path_references':14,'body_bytes':1934,'physical_bytes':2172,'noncode_bytes':238,'reachable_instructions':686,'direct_body_calls':140,'internal_direct_body_calls':23,'external_direct_body_calls':117,'indirect_body_calls':10,'bounded_indirect_body_calls':10,'direct_bl_entry_sites':680,'stored_entry_pointers':3,'raw_interior_word_collisions':1,'strict_interior_ingress':0},'behavior':{'kernel_bootstrap_and_thread_creation':True,'thread_registry_lifecycle':True,'ten_slot_registered_callback_dispatch':True,'event_flag_and_tick_housekeeping':True},'provider_boundary':{'easylogger_calls':72,'cmsis_freertos_calls':30,'freertos_assert_calls':3,'littlefs_port_calls':1,'closed_first_party_calls':9,'bounded_first_party_calls':2,'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','littlefs_backend_baseline_commit':'0494ce7169f06a734a7bd7585f49a9fa91fa7318','cmsis_wrappers':['osKernelInitialize','osKernelStart','osKernelGetTickCount','osThreadNew','osThreadGetId','osThreadSetPriority','osThreadTerminate','osThreadFlagsSet','osThreadFlagsWait','osEventFlagsNew','osEventFlagsSet','osEventFlagsWait'],'historical_thread_manager_commit':None,'new_version_discriminator':False,'private_generating_commit_recoverable':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
