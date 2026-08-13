#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for thread_pool.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-thread-pool-function-map.tsv';PM=ROOT/'tools/manifests/g2-thread-pool-provider-map.tsv';CL=ROOT/'tools/manifests/g2-thread-pool-closure.tsv'
PINS={FM:'edca26ac6d46d38334572539350f9b1e949483c1b70d609e17a52db90a3ae1ce',PM:'5a1702bcec7361adf7687744455a92207d2d8edde887d200fdc270437328ac05',CL:'d6664d69d9752f9a46e98b44008d7310cdc98b69eb31ab2baa02c2c910f27cf1'}
PHYS=(0x49110C,0x4916B8);PATH=0x7073A4;CELL=0x491624
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490E2,0x44971C,0x4497B6,0x44981C,0x44986E,0x449A32,0x449ABE,0x449B3C,0x449BEC};FREERTOS={0x5FA0A4};IAR={0x439C04,0x43C0E4,0x44B728,0x48D540}
STORED=[(0x49169C,0x49110C)];RAW=[(0x585C31,0x4915D0)];IND=[0x491180]
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
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=3 or sum(r['source_path_anchor']=='yes' for r in rows)!=2 or sum(r['ghidra_discovered']=='yes' for r in rows)!=2:raise c.AuditError('function inventory changed')
 starts={a for a,_ in F};ins={};calls=[];ind=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=1290 or sh(body)!='9c2941946bcf4461fe4cee9d1df5be29f26847f8932be7dbfd96d6cb9abc1308' or code!=body or len(ins)!=463 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='06a44d1794bc8b12d5ce12756a7fff4868e831e9c619e8a36d537e1df7cc5236' or ind!=IND:raise c.AuditError('instruction closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=162 or sh(non)!='3620f0bbf469141fe26057bbcdc42427578e819b2b775297ef9016c88439da22' or sh(c._slice(b,*PHYS))!='a8140e215ccba8535685d8e44dbbae789d0e63cc24b1b0ab333bd07653de26e9':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='14bd6b50a2215bd343e3795518145640769d13f3404333b8ab4d16759282b766' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='7c05c97abb128ee9f586dec9aa88bbcab568e02e8a50940767092e504e4ecf7c':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS,IAR)
 if len(calls)!=78 or sum(y in starts for _,y in calls)!=0 or c._pair_digest(calls)!='3fd397642e783ec362b1d48655f85b1a828a68c4a26740228df7fb59957c8ce7' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(60,10,2,6):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non_bl=[];wide=[];wstrict=[];inter_i=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter_i:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non_bl.append((a,y))
  x,z=struct.unpack('<HH',c._slice(b,a,a+4));y=wide_branch_target(a,x,z)
  if y in starts:wide.append((a,y))
  elif y in inter_i:wstrict.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!='1eb12f89e650ced7c33e059ebecfece44d4d711444d750f53462ff76ed2d5196' or strict or non_bl or wide or wstrict:raise c.AuditError('branch ingress changed')
 stored=[];raw_p=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0]
  if v&1 and (v&~1) in starts:stored.append((c.BASE+off,v&~1))
  elif v&1 and (v&~1) in inter_i:raw_p.append((c.BASE+off,v&~1))
 if stored!=STORED or c._pair_digest(stored)!='72f8e6cf5f64c4ba9d4ad5b4fdd6433b1dc1d15f4c1fb1581ee39c1f919fc3ac' or raw_p!=RAW or c._pair_digest(raw_p)!='927d7f8ab14b52e6156e778ee77ed9064bb844fde3a56805e292bbcc6f64c623':raise c.AuditError('stored ingress changed')
 expected=r'D:\01_workspace\s200_ap510b_iar_git\framework\sync\thread_pool.c'
 if cstr(b,PATH)!=expected or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=[(CELL,x) for x in t.literal_references(b,CELL)]
 if len(refs)!=12 or c._pair_digest(refs)!='171be20876b8250bf7ef574b6feeced02ababdeeee215a1c98f23b090ea2056c':raise c.AuditError('path references changed')
 routed=any('thread_pool' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 if routed:raise c.AuditError('unimplemented thread pool entered production overlay')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure; corpus-independent','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'framework\sync\thread_pool.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':3,'ghidra_discovered_functions':2,'restored_functions':1,'path_anchored_functions':2,'raw_path_references':12,'body_bytes':1290,'physical_bytes':1452,'noncode_bytes':162,'reachable_instructions':463,'direct_body_calls':78,'internal_direct_body_calls':0,'external_direct_body_calls':78,'indirect_body_calls':1,'bounded_indirect_body_calls':1,'direct_bl_entry_sites':18,'stored_entry_pointers':1,'raw_interior_word_collisions':1,'strict_interior_ingress':0},'behavior':{'worker_thread_queue_dispatch':True,'pool_creation_with_mutex_and_queue':True,'job_submission_and_callback':True},'provider_boundary':{'easylogger_calls':60,'cmsis_freertos_calls':10,'freertos_assert_calls':2,'iar_dlib_calls':6,'first_party_calls':0,'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','cmsis_wrappers':['osThreadNew','osMutexNew','osMutexAcquire','osMutexRelease','osMutexDelete','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet','osMessageQueueDelete'],'historical_thread_pool_commit':None,'new_version_discriminator':False,'private_generating_commit_recoverable':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
