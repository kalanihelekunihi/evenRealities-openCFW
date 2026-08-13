#!/usr/bin/env python3
"""Fail-closed object/provider audit for ux_wear_detect.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-ux-wear-detect-function-map.tsv';PM=ROOT/'tools/manifests/g2-ux-wear-detect-provider-map.tsv';CL=ROOT/'tools/manifests/g2-ux-wear-detect-closure.tsv'
PINS={FM:'270b10a6ed221e92cd9903837958b2e09bde336d9cff74c887fdeeeb127c6f66',PM:'54bffb54fa7529be65634f2bfd5592d6a331df7f2e2e503931e4099a75bc9ab0',CL:'41b3477f5fa015d64b7a0aa9725ed5d58522c4b008b870651fdaebd505aa6ff4'}
PHYS=(0x49EAD8,0x49F020);PATH_CELL=0x49EFB8;PATH_RUN=0x6F7CF0
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};CMSIS={0x4490CC};NANOPB={0x48EB32}
FIRST={0x45A568,0x464D1C,0x46805A,0x46B0EC,0x46B44C,0x47243A,0x474100,0x47432C,0x47E320,0x4AC16C,0x502BF0,0x502DAE}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('nanopb changed')
 if 'd213f261b5be6bb29a7cce8b84071706b72f4d53' not in (ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text():raise c.AuditError('CMSIS-FreeRTOS changed')
 iar=(ROOT/'docs/research/iar-dlib-runtime-census.md').read_text()
 if '9.20 is therefore a practical lower bound' not in iar or '9.60.2' not in iar:raise c.AuditError('IAR changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 provenance()
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=7 or sum(r['source_path_anchor']=='yes' for r in rows)!=3:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1236 or sh(body)!='4b222b77a80b3e4f97449dabb8488bed17da7925e34d1c152ef5330210f2c777' or len(ins)!=490 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='860cb59bcc198df5a7959e4c55de28f2a503726897a47bda8bb5dc3220c0de36' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=116 or sh(non)!='9659fd8a4bd5654bc4fa5e9c529c069749130809f26637c2a51f25ebc269954d' or sh(c._slice(b,*PHYS))!='ed6d2af7bad86b9ae929fee81c7b97f437be81e6a2657bf95eb42821d450a66a':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='d134c028548871d11dd9d5966ca59423536f2ce3a51e4001c81c75a01f43ace2' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='77ded4128b8393ee5a4f27cb780776875f4e2c77b60ed2836c7fd982e3b3002c':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,NANOPB,FIRST)
 if len(calls)!=84 or sum(y in starts for x,y in calls)!=13 or c._pair_digest(calls)!='f9204e419bc54cd727b3fdcb599f1f3c538887f7407df6171a1b191ef8b776c8' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(45,2,2,1,21):raise c.AuditError('call closure changed')
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=22 or c._pair_digest(entries)!='012ac6f63fde762c05bd923280d37790c13e554cd2505b6740a0a4ed7488b672' or strict or unknown:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if stored!=[(0x6A4754,0x49ED05)] or c._pair_digest(stored)!='1d47119137d22ca868b50eb4d4ae4a188dce300f5b86d717f3da79d2e453a397' or interior:raise c.AuditError('stored ingress changed')
 if cstring(b,PATH_RUN)!=r'D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_wear_detect\ux_wear_detect.c' or struct.unpack_from('<I',b,PATH_CELL-c.BASE)[0]!=PATH_RUN:raise c.AuditError('path changed')
 pairs=[(x,PATH_CELL) for x in t.literal_references(b,PATH_CELL)]
 if len(pairs)!=9 or c._pair_digest(pairs)!='a7d8f8b660e94bab1b209b44d715df798523d3d9b9f373d1f2d0785c9f8b04bd':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('ux_wear_detect' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\ux\ux_wear_detect\ux_wear_detect.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':7,'ghidra_discovered_functions':3,'restored_functions':4,'path_anchored_functions':3,'body_bytes':1236,'physical_bytes':1352,'noncode_bytes':116,'reachable_instructions':490,'direct_body_calls':84,'internal_direct_body_calls':13,'external_direct_body_calls':71,'indirect_body_calls':0,'direct_bl_entry_sites':22,'stored_function_entry_pointers':1,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':45,'iar_dlib_calls':2,'cmsis_freertos_calls':2,'nanopb_calls':1,'first_party_calls':21,'cmsis_freertos_seams':['osKernelGetTickCount'],'freertos_kernel_seams':[],'historical_wear_detect_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
