#!/usr/bin/env python3
"""Fail-closed object/provider audit for generic_animation.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-generic-animation-function-map.tsv';PM=ROOT/'tools/manifests/g2-generic-animation-provider-map.tsv';CL=ROOT/'tools/manifests/g2-generic-animation-closure.tsv'
PINS={FM:'97d9f04c92bb8bebee5a04366a7c68bb5c6513a16c233ace432824c029d1d0ad',PM:'9a1e4cf029099d9344afcd9d6f7b1de1a953a930db778d65afdd7c1989cee7b4',CL:'7cd0702761788a06414693fa4a534ea241649b080c5bd55b7b35daf405496564'}
PHYS=(0x463C68,0x464330);PATH_CELL=0x4642C8;PATH_RUN=0x6FAD0C
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};CMSIS={0x4490CC};HEAP={0x474CD2,0x474D16}
LVGL={0x43DFA4,0x43E2EA,0x43F506,0x43F568,0x44127E,0x44129E,0x441488,0x44D7B8,0x4503D6,0x450408,0x4506CE,0x498680}
FIRST={0x45A568,0x464C36,0x498668}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise c.AuditError('LVGL changed')
 if 'd213f261b5be6bb29a7cce8b84071706b72f4d53' not in (ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text():raise c.AuditError('CMSIS-FreeRTOS changed')
 if 'deff9ab509341f264addbd3c8ada533678591905' not in (ROOT/'third_party/tlsf/README.openCFW.md').read_text():raise c.AuditError('TLSF changed')
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
 if len(F)!=17 or sum(r['source_path_anchor']=='yes' for r in rows)!=4:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1622 or sh(body)!='19729856a2eee1fa110ecde868db1eb6fa03c2dcb43ff8ae8e845de25db99f6d' or len(ins)!=684 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='378507228e85ecfe97046182f711511f07223cb2679fa21ee8eb8fbe45a07c9c' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=114 or sh(non)!='5c3fa924f1f5d79b44ee28e5c4aea2330d8be4fe3054b462804b4d3b87feec2b' or sh(c._slice(b,*PHYS))!='b0217ae743fa75b234c7e39e8157b5ccddc78b3f4ac00343f542f2304b714324':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='c588f1bce8f6fd11c0d01189874cfd1275ca0a353f9fc8033d5415c03635155a' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='6332f837320bfe10cba8cd62a38b030979d3fa699c9aaf5b33ef7520d5543d61':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,CMSIS,HEAP,LVGL,FIRST)
 if len(calls)!=82 or sum(y in starts for x,y in calls)!=2 or c._pair_digest(calls)!='7533a27f6d539914a157f6e6c87b7691fd7f1f2db81b79a490151497ea973c4a' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(40,4,3,3,27,3):raise c.AuditError('call closure changed')
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=90 or c._pair_digest(entries)!='f8742cf0e2356e5e3495a36f8fcdd7f3818025571674b113f998fac6ce5deffe' or strict or unknown:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};hits=[(a,v) for a,v in words if v in enc];stored=[(a,v) for a,v in hits if a%4==0];collisions=[(a,v) for a,v in hits if a%4];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if stored!=[(0x4642F4,0x4640FF),(0x4642FC,0x4640C1),(0x464318,0x464153),(0x464320,0x46415F)] or c._pair_digest(stored)!='bc463910df5a0e2619df59692c7b9e3d7b8cef30bd5646a4aed06e6b28b44d5e':raise c.AuditError('stored ingress changed')
 if len(collisions)!=5 or c._pair_digest(collisions)!='7cc6b177d5654f1d400a9671006cd1112e0b796d4ab819e9d72bd85fc5a6b616' or len(interior)!=32 or c._pair_digest(interior)!='46bec2ff0659fc693babb6f23cd19063f85fd9e1341c218940f8bb89449bb89c':raise c.AuditError('raw word collision closure changed')
 if cstring(b,PATH_RUN)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\common\generic_animation.c' or struct.unpack_from('<I',b,PATH_CELL-c.BASE)[0]!=PATH_RUN:raise c.AuditError('path changed')
 pairs=[(x,PATH_CELL) for x in t.literal_references(b,PATH_CELL)]
 if len(pairs)!=8 or c._pair_digest(pairs)!='fe6f8f4336ca3ed245bdfbb55cf4a8b24f6aed9ebc94d9e3b5c506cf8ee03a45':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('generic_animation' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\common\generic_animation.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':17,'ghidra_discovered_functions':4,'restored_functions':13,'path_anchored_functions':4,'body_bytes':1622,'physical_bytes':1736,'noncode_bytes':114,'reachable_instructions':684,'direct_body_calls':82,'internal_direct_body_calls':2,'external_direct_body_calls':80,'indirect_body_calls':0,'direct_bl_entry_sites':90,'stored_function_entry_pointers':4,'unaligned_start_word_collisions':5,'raw_instruction_word_interior_collisions':32,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':40,'iar_dlib_calls':4,'cmsis_freertos_calls':3,'source_owned_heap_calls':3,'lvgl_calls':27,'first_party_calls':3,'cmsis_freertos_seams':['osKernelGetTickCount'],'freertos_kernel_seams':[],'historical_generic_animation_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
