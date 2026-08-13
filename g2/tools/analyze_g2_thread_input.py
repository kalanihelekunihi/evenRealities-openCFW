#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for thread_input.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-thread-input-function-map.tsv';PM=ROOT/'tools/manifests/g2-thread-input-provider-map.tsv';CL=ROOT/'tools/manifests/g2-thread-input-closure.tsv'
PINS={FM:'44b1e9efb28a2d88e45536655eeab7a1b20962fc9af6fa7fc736ebfbd8135160',PM:'d5817307a647d8bd7e0e5ca62812a2a2e33c842116c624deb15b558479a19adc',CL:'cf5fef45f9b718e9bad5e5123567d6b538796c2aef87fef91cee3badbc6e9984'}
PHYS=(0x512C84,0x51357C);PATH_ADDR=0x7072D8;CELL=0x5134C4
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4};CMSIS={0x4490E2,0x4491FE,0x449238,0x4492C2,0x449376,0x449A32,0x449ABE,0x449B3C,0x449BEC};RUNTIME={0x4733EE};TM={0x4C9B86,0x4C9BE2,0x4C9C3C};CLOSED_FP={0x472362,0x47D8E4,0x4ABE60,0x502AE8,0x502B4A,0x502B5A,0x502BF0,0x502EF4,0x56110C};OPEN_FP={0x480D72,0x4D3554,0x55B64A,0x55B66A,0x55B6DC,0x55B730,0x55B840,0x55B92A}
STORED=[(0x7940E8,0x512CBD)]
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
 if len(F)!=23 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort()
 if len(body)!=2090 or sh(body)!='f5424e670bf76b7044cdfbdd4ae7f1f44630d56aa5522bf982856c9e97f9dd55' or len(ins)!=785 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='b2360d17d4068f27b623eb52a0b6ae0c97e8c12619ba15f035d9f5f27444fc86' or ind!=[0x512FC6]:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=206 or sh(non)!='a587e90a73dae96f13b85a3b3a5f96c80b75bc4fc8f17828b248569ab5551a06' or sh(c._slice(b,*PHYS))!='cfeeef6ebfef4215bfdbb8264d21ee026eca20d3015351327dde42a8a3cce272':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='e30dbe2ba2c025beafe49e66ea1c4c788a86d3269e645a64c122318d3b1415c6' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='29e9f822ce0b6cd07b0eb190d397d034c6174d59a38fbd377f18c630ae925bf0':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,RUNTIME,TM,CLOSED_FP,OPEN_FP)
 if len(calls)!=140 or sum(y in starts for x,y in calls)!=13 or c._pair_digest(calls)!='c25dbbe6749b7f90b78c07e1be2a2489763b059478a6b0e253c2bf97064581a0' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(90,3,10,1,3,9,11):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[];ientries=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in ientries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=20 or c._pair_digest(entries)!='3a362cb22181f771b2bc2b05ff430631c930503a64d9ece1cae04700d75deff1' or strict or pseudo:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in ientries]
 if stored!=STORED or interior:raise c.AuditError('stored ingress changed')
 o=PATH_ADDR-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0 or b[o:e].decode('ascii')!=r'D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_input.c':raise c.AuditError('path changed')
 refs=t.literal_references(b,CELL);pairs=[(CELL,x) for x in refs]
 if len(refs)!=18 or c._pair_digest(pairs)!='1558498896a9fc5b30783613847ef3f3ea1d8678008960ddff77ea3b7337fb61':raise c.AuditError('path refs changed')
 if any('thread_input' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\threads\thread_input.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':23,'ghidra_discovered_functions':5,'restored_functions':18,'path_anchored_functions':5,'body_bytes':2090,'physical_bytes':2296,'noncode_bytes':206,'reachable_instructions':785,'direct_body_calls':140,'internal_direct_body_calls':13,'external_direct_body_calls':127,'indirect_body_calls':1,'direct_bl_entry_sites':20,'external_direct_bl_entry_sites':7,'stored_function_entry_pointers':1,'strict_interior_ingress':0},'behavior':{'cmsis_thread_lifecycle':True,'queue_record_dispatch':True,'bounded_handler_table_dispatch':True,'touch_gesture_mode_policy':True},'provider_boundary':{'easylogger_calls':90,'iar_dlib_calls':3,'cmsis_freertos_calls':10,'source_owned_runtime_wrapper_calls':1,'closed_thread_manager_calls':3,'closed_first_party_calls':9,'bounded_open_first_party_calls':11,'freertos_kernel_direct_calls':0,'cmsis_wrappers':['osThreadNew','osThreadTerminate','osThreadFlagsSet','osThreadFlagsWait','osDelay','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet','osMessageQueueDelete'],'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
