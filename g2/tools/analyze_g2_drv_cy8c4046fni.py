#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for drv_cy8c4046fni.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-drv-cy8c4046fni-function-map.tsv';PM=ROOT/'tools/manifests/g2-drv-cy8c4046fni-provider-map.tsv';CL=ROOT/'tools/manifests/g2-drv-cy8c4046fni-closure.tsv'
PINS={FM:'17278ba569b6f6b8815d22b306cf431041b77bfc84e4eac4850613c7883eac40',PM:'15d30a5a045ceb6ae871c5a43aad6cd06e438a7f363c92407dc14e7f2bf7cc5a',CL:'1a3f94eb3fb964a806983d00cd7ba948270b8b22bcda7a5a6388a6db46d71733'}
PHYS=(0x55B2EC,0x55BA70);PATH=0x702328;CELL=0x55B9D0
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};CMSIS={0x449376};HAL={0x50436E,0x5044B4,0x5045C0,0x50468E};FIRST={0x53A5BE}
STORED=[(0x55B9F0,0x55B2EC),(0x55B9F4,0x55B304),(0x55B9F8,0x55B31C),(0x55B9FC,0x55B32E)];IND=[0x55B356,0x55B370,0x55B38A,0x55B3A4,0x55B3D2,0x55B452,0x55B45E,0x55B55A,0x55B6C4]
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
 if 'physical_interval\t[0x0055A558,0x0055B2A4)' not in (ROOT/'tools/manifests/g2-pb-service-health-closure.tsv').read_text():raise c.AuditError('preceding health-service boundary regressed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=23 or sum(r['source_path_anchor']=='yes' for r in rows)!=7 or sum(r['ghidra_discovered']=='yes' for r in rows)!=20:raise c.AuditError('function inventory changed')
 starts={a for a,_ in F};ins={};calls=[];ind=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=1754 or sh(body)!='e57315793f123c87bef9ff871ead897585e7b6ad99be934fbc1b3c81d1dbfa2b' or code!=body or len(ins)!=708 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='6283cd4ea10462d17ad28050a5cb7735464caab4483bb9a7433e265865fd80c0' or sorted(ind)!=IND:raise c.AuditError('instruction closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=170 or sh(non)!='246f1a4563ff6ae7319ecfc22d846d7d59bb80933ec50bb6501a8c4440199f9b' or sh(c._slice(b,*PHYS))!='f332ef2582b13694469bc6a64e0e6089077b990338848a23a7d60de28412ffab':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='e543893207979b453e3f9af88db4ec98e4b12721562afd2aecd050a73fb8ff13' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='a208dbf69f0a4bca850b86b51d5156ec070b9973ecfef03ee0b4b782c9b4d94d':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,HAL,FIRST)
 if len(calls)!=87 or sum(y in starts for _,y in calls)!=10 or c._pair_digest(calls)!='eb33483ed56a21475a26b0aa2ddafd1d7ccecdb5ce3a40197686931d22b755ea' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(60,9,2,4,2):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non_bl=[];wide=[];wstrict=[];inter_i=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter_i:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non_bl.append((a,y))
  x,z=struct.unpack('<HH',c._slice(b,a,a+4));y=wide_branch_target(a,x,z)
  if y in starts:wide.append((a,y))
  elif y in inter_i:wstrict.append((a,y))
 if len(entries)!=50 or c._pair_digest(entries)!='4200f389488dc08d13199f1d896cc6cc3b92355a25f76aec4e9beb48ba82892d' or strict or non_bl or wide or wstrict:raise c.AuditError('branch ingress changed')
 stored=[];raw_p=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0]
  if v&1 and (v&~1) in starts:stored.append((c.BASE+off,v&~1))
  elif v&1 and (v&~1) in inter_i:raw_p.append((c.BASE+off,v&~1))
 if stored!=STORED or c._pair_digest(stored)!='7323684ef3f7c757b6cb5dfc846cfa0f2832ab8f6eee737214232b9d52dcf92c' or raw_p:raise c.AuditError('stored ingress changed')
 expected=r'D:\01_workspace\s200_ap510b_iar_git\driver\touch\drv_cy8c4046fni.c'
 if cstr(b,PATH)!=expected or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=[(CELL,x) for x in t.literal_references(b,CELL)]
 if len(refs)!=12 or c._pair_digest(refs)!='b8cec35125289c5d9529500161740cbaf8d293d80c22175645624526835d0a29':raise c.AuditError('path references changed')
 routed=any('cy8c4046fni' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 if routed:raise c.AuditError('unimplemented touch driver entered production overlay')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure; corpus-independent','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'driver\touch\drv_cy8c4046fni.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':23,'ghidra_discovered_functions':20,'restored_functions':3,'path_anchored_functions':7,'raw_path_references':12,'body_bytes':1754,'physical_bytes':1924,'noncode_bytes':170,'reachable_instructions':708,'direct_body_calls':87,'internal_direct_body_calls':10,'external_direct_body_calls':77,'indirect_body_calls':9,'bounded_indirect_body_calls':9,'direct_bl_entry_sites':50,'stored_entry_pointers':4,'raw_interior_word_collisions':0,'strict_interior_ingress':0},'behavior':{'i2c_ops_table_dispatch':True,'controller_init_and_reset':True,'touch_report_and_gesture_extraction':True,'four_entry_driver_callback_table':True},'provider_boundary':{'easylogger_calls':60,'iar_dlib_calls':9,'cmsis_freertos_calls':2,'closed_hal_i2c_calls':4,'bounded_first_party_calls':2,'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','cmsis_wrappers':['osDelay'],'public_cypress_source_candidate':None,'historical_drv_cy8c4046fni_commit':None,'new_version_discriminator':False,'private_generating_commit_recoverable':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
