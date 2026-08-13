#!/usr/bin/env python3
"""Fail-closed object/provider audit for fade_anim.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-fade-anim-function-map.tsv';PM=ROOT/'tools/manifests/g2-fade-anim-provider-map.tsv';CL=ROOT/'tools/manifests/g2-fade-anim-closure.tsv'
PINS={FM:'56718c968651f0caff18a6d3d99eb1cffc8adda3598cdeb0693f7ecd3988a6c5',PM:'4449926b362de442b07d43cf2bb4be0a46e3b1897867c5ea3e35ee5d6426e9a0',CL:'da4cf5f2cc0a46835277b7f8f3efd802fcb8add8c7b5ba46e9b71234c2c044f8'}
PHYS=(0x58C12C,0x58C836);PATH_CELL=0x58C740;PATH_RUN=0x70BF64
EASY={0x43CE9E,0x43D0CE,0x43D574}
LVGL={0x43E2D4,0x44104C,0x441068,0x44127E,0x44129E,0x44130C,0x4413CE,0x44140E,0x441488,0x44DCE2,0x44DDEA,0x4503D6,0x450408,0x450500,0x4506CE,0x597E90,0x597EA6,0x597EE0,0x597F10,0x597F52,0x597F82}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text():raise c.AuditError('LVGL changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 provenance()
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=11 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1678 or sh(body)!='ff177c5f6eb70ae91f96f96ee56dc41fa3c52a03196f37b2ff9feb301d3bf86e' or len(ins)!=660 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='a18a93efd636db809f423c7f617fc514cca789d6006cf5b8327a654a8f4b7ee6' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=124 or sh(non)!='9c418c79e4f78b0d50c1f8f91ef3d233f744e48724ef207cb908782f1814a4f3' or sh(c._slice(b,*PHYS))!='d7d70d0046d2519c2b1027f4119374d8acabbbbdaaada3cad0ec5ebf0ce641ad':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='d86880a315bd247b67b44e82f2abd0b48aa7872dbb217da613d922c8e7569392' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='c4ee5bc7bcad5c8e2f9a6255922f1675a9ab4539af30a89ec93b6d6f9297deb7':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL)
 if len(calls)!=92 or sum(y in starts for x,y in calls)!=3 or c._pair_digest(calls)!='970f05cd6cb8342488d0a58bd6e6f58176b1dcff73222af0cff2a8fa2901b208' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(45,44):raise c.AuditError('call closure changed')
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=38 or c._pair_digest(entries)!='51545c09199013832815624b2863138885fc1e5cc747af9f4d037960c33145d4' or strict or unknown:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if(v&1)and(v&~1)in inter]
 if stored!=[(0x58C74C,0x58C12D),(0x58C798,0x58C231)] or c._pair_digest(stored)!='76a20ae4217bb2f304d3dbdd18c2a53c189ff26205e7f2dcbe0b384745eb5a49' or interior:raise c.AuditError('stored ingress changed')
 if cstring(b,PATH_RUN)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\anim\fade_anim.c' or struct.unpack_from('<I',b,PATH_CELL-c.BASE)[0]!=PATH_RUN:raise c.AuditError('path changed')
 pairs=[(x,PATH_CELL) for x in t.literal_references(b,PATH_CELL)]
 if len(pairs)!=9 or c._pair_digest(pairs)!='d999af9cd12566ecec6a28440c0fa9498d03e7bb59db19f61d08e9aeb5c93356':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('fade_anim' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\anim\fade_anim.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':11,'ghidra_discovered_functions':5,'restored_functions':6,'path_anchored_functions':5,'body_bytes':1678,'physical_bytes':1802,'noncode_bytes':124,'reachable_instructions':660,'direct_body_calls':92,'internal_direct_body_calls':3,'external_direct_body_calls':89,'indirect_body_calls':0,'direct_bl_entry_sites':38,'stored_function_entry_pointers':2,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':45,'lvgl_calls':44,'cmsis_freertos_seams':[],'freertos_kernel_seams':[],'historical_fade_anim_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
