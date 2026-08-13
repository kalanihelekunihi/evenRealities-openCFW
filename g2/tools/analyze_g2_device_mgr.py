#!/usr/bin/env python3
"""Fail-closed object/provider audit for device_mgr.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-device-mgr-function-map.tsv';PM=ROOT/'tools/manifests/g2-device-mgr-provider-map.tsv';CL=ROOT/'tools/manifests/g2-device-mgr-closure.tsv'
PINS={FM:'d3e064f5dc4d38ca1db018d99fdeee23625a8253c8a13621d1436dffaa1084ac',PM:'687ecb1056266f12cf5c393d6f6dc53b211d638f9a28d68039c1ae731c137c24',CL:'bf7d278d22024a50981ff64b8b8f606e230eafe559c1db8fdb28d300377bd08e'}
F=((0x4C6240,0x4C632C),(0x4C632C,0x4C6498),(0x4C6498,0x4C64A4),(0x4C64A4,0x4C64C8),(0x4C64C8,0x4C6510),(0x4C6510,0x4C659A),(0x4C659A,0x4C661C),(0x4C661C,0x4C6638),(0x4C6638,0x4C66F0),(0x4C66F0,0x4C674C),(0x4C674C,0x4C67A4),(0x4C67A4,0x4C67DC),(0x4C67DC,0x4C6810),(0x4C6810,0x4C691C),(0x4C691C,0x4C6990),(0x4C6990,0x4C69F4),(0x4C69F4,0x4C6A56),(0x4C6A56,0x4C6A9E),(0x4C6A9E,0x4C6AD8),(0x4C6AD8,0x4C6BF4))
PHYS=(0x4C6240,0x4C6D04);POOL=(0x4C6BF4,0x4C6D04);PATH=0x6F9C74;CELL=0x4C6BFC
ANCHORS={0x4C659A,0x4C6810,0x4C691C,0x4C6AD8};GHIDRA=ANCHORS
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490E2,0x4491FE,0x449376,0x4493B0,0x449498,0x449A32,0x449ABE,0x449B3C};FREERTOS={0x454EFE};IAR={0x439C04}
CLOSED={0x443484,0x44349C,0x4434B4,0x4442D0,0x4487AC,0x44A19A,0x464C36,0x466660,0x46BE10,0x4ABE60,0x4ACF7C,0x4AD06C,0x4AD45C,0x4AF11C,0x4FF8D4,0x4FF8DC,0x4FF8E4,0x502BF0,0x51283C,0x5128A0,0x512A70,0x52F2E0,0x53AE66,0x53C0F4,0x53CA10,0x53CA32}
BOUNDED={0x45A568,0x4AC02A,0x4AC0F8,0x4AC75A,0x50938E,0x510FE2,0x52F38C,0x53A09C,0x53A5BE}
TBL=0x7490C4;HANDLERS=(0x53A0B7,0x4C6639,0x4AC279,0x4C66F1,0)
STORED=[(0x7490D0,0x4C6639),(0x7490E0,0x4C66F1),(0x791BCC,0x4C6241),(0x791BD0,0x4C64A5)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstr(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());cms=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text());kernel=json.loads((ROOT/'third_party/freertos-kernel/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cms['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53' or cms['upstreams']['cmsis_5']['selected_commit']!='2b7495b8535bdcb306dac29b9ded4cfb679d7e5c' or kernel['upstream']['selected_commit']!='def7d2df2b0506d3d249334974f51e427c17a41c':raise c.AuditError('provider provenance changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 fs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if tuple(fs)!=F or len(rows)!=20 or sum(r['source_path_anchor']=='yes' for r in rows)!=4 or sum(r['ghidra_discovered']=='yes' for r in rows)!=4:raise c.AuditError('function inventory changed')
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  if set(ins)&set(ii):raise c.AuditError('overlap')
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=2484 or sh(body)!='e4ac2fc2209bbdeaf3a277326bffba4128026e147cfce4597006eac11bb82c1f' or code!=body or len(ins)!=931 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='58bc559620a687096d4f887818c7b4814481580e08493591b84ff88c15ad3c83' or ind!=[0x4C6544]:raise c.AuditError('instruction closure changed')
 tbl=[struct.unpack('<I',c._slice(b,TBL+8*i+4,TBL+8*i+8))[0] for i in range(5)]
 if tbl!=[0x53A0B7,0x4C6639,0x4AC279,0x4C66F1,0] or (HANDLERS[1]&~1 not in starts) or (HANDLERS[3]&~1 not in starts):raise c.AuditError('indirect dispatch table changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=272 or sh(non)!='a5a17a73cb02190a56d3c794a1c35570023cbe075a87b047cc4a40fa7b696486' or non!=c._slice(b,*POOL) or sh(c._slice(b,*PHYS))!='7e45a3a41851f1558a538be5e4eaf57dcefe1bf5a9f60d20a984a29e81bee93c':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='1507733543119d68b4a80182cf26f2ec17d9132c5f90ed0282c0579c1f250dbb' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='832ac49c8104ea3bd56ef50c4aca6951c6fdeb61d910653b1f08d1ba26415459':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS,IAR,CLOSED,BOUNDED)
 if len(calls)!=152 or sum(y in starts for x,y in calls)!=15 or c._pair_digest(calls)!='11d3172199d54098494409ae1ce97848be50c8226b68e7b3ec0e04114f3dc903' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(75,10,1,3,34,14):raise c.AuditError('call closure changed')
 entries=[];strict=[];pseudo=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:pseudo.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!='ab6069b62c103bff5e18621a4bf0e8e8d1755534edcbed40eb0eb7bb86fae15a' or strict or pseudo:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];rawcol=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored!=STORED or rawcol!=[(0x509985,0x4C6AB5)]:raise c.AuditError('stored ingress changed')
 if cstr(b,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\platform\device_mgr\device_mgr.c' or struct.unpack('<I',c._slice(b,CELL,CELL+4))[0]!=PATH:raise c.AuditError('retained path changed')
 refs=t.literal_references(b,CELL)
 if len(refs)!=15 or sum(any(a<=x<z for x in refs) for a,z in F)!=8 or c._pair_digest([(CELL,x) for x in refs])!='0ed8b547df3a2d62d8789281b3c7d4a5a7ade72139c8fa82370484cd8383f05f':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('device_mgr' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'platform\device_mgr\device_mgr.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':20,'ghidra_discovered_functions':4,'restored_functions':16,'path_anchored_functions':4,'raw_path_references':15,'body_bytes':2484,'physical_bytes':2756,'noncode_bytes':272,'reachable_instructions':931,'direct_body_calls':152,'internal_direct_body_calls':15,'external_direct_body_calls':137,'indirect_body_calls':1,'bounded_indirect_body_calls':1,'direct_bl_entry_sites':18,'stored_aligned_function_entry_pointers':4,'raw_interior_word_collisions':1,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':75,'cmsis_freertos_calls':10,'freertos_kernel_calls':1,'iar_dlib_calls':3,'closed_first_party_calls':34,'bounded_first_party_calls':14,'cmsis_freertos_seams':['osThreadNew','osThreadTerminate','osDelay','osTimerNew','osTimerStart','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet'],'freertos_kernel_seams':['xTaskGetTickCount'],'cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','freertos_kernel_commit':'def7d2df2b0506d3d249334974f51e427c17a41c','cmsis_5_commit':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','historical_device_mgr_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
