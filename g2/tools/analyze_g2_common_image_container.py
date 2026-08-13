#!/usr/bin/env python3
"""Fail-closed object/provider audit for common_image_container.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-common-image-container-function-map.tsv';PM=ROOT/'tools/manifests/g2-common-image-container-provider-map.tsv';CL=ROOT/'tools/manifests/g2-common-image-container-closure.tsv'
PINS={FM:'971ba938349370d6d56f3761d109cf89fea2e57dd64fb72766b7725d483c11d2',PM:'b4b332826951d4cc0be91928d2e7c5d01d9d2b5a68d5941962f6deb2e4f687f2',CL:'a59715d354d47aece83e0f1a91e3cb6df8db98d37f4cdd8aa0c59aad931c4fea'}
PHYS=(0x4DC5AE,0x4DCCD8);EASY={0x43CE9E,0x43D0CE,0x43D574};LVGL={0x440656,0x441068,0x44D7B8};HEAP={0x474D16};CACHE={0x47510E};ABS={0x509694};FIRST={0x498680,0x5456D6}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('LVGL changed')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=3 or sum(r['source_path_anchor']=='yes' for r in rows)!=2:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=1554 or sh(body)!='68e77fb7d59cae1d99b6ad68731cff371cc47cb111c30cc3b05341b098023ed9' or len(ins)!=591 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='3632afab86c26e7f25e134e6d4c7c146b9d0120a5075959fbf6dbc71d0db3ac1' or ind:raise c.AuditError('instruction closure changed')
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 non+=c._slice(b,p,PHYS[1])
 if len(non)!=280 or sh(non)!='1c18922a2272bd70cb526b30d051ff5b9dc3b531705a150d062b899b4f655e6f' or sh(c._slice(b,*PHYS))!='06fa573f6d72050ec84578e2f3ec035bffd3f5eaa02319896f0af1129b039220':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='19cf353c508703694c389ef2ff7355ffe01ed756b165f9f096badf3940a09c59' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='5c319296e0affa17c3ee47eb496335ba41202da3a6e8b053e874a128425eaaeb':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);groups=(EASY,LVGL,HEAP,CACHE,ABS,FIRST)
 if len(calls)!=81 or sum(y in starts for x,y in calls)!=1 or c._pair_digest(calls)!='9325316d2c20d56aef31637de829eed8e1fc9375b25a9ce67953576fc3cde5d8' or set(ext)!=set().union(*groups) or tuple(sum(ext[x] for x in s) for s in groups)!=(70,3,3,1,1,2):raise c.AuditError('provider closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=3 or c._pair_digest(entries)!='ba36d2e2129d20d03e28fcb82ebd9cf4cdc51de28ee9e49577f48b12f63f3be5' or strict:raise c.AuditError('BL ingress changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 if [(a,v) for a,v in words if v in enc] or [(a,v) for a,v in words if (v&1)and(v&~1)in inter]:raise c.AuditError('stored ingress changed')
 pairs=[]
 for cell in (0x4DCA20,0x4DCC54):pairs += [(cell,x) for x in t.literal_references(b,cell)]
 if len(pairs)!=28 or c._pair_digest(pairs)!='3f2ab00da3f37e0c74d1d5f27ffcbce6950b1c6d5a7dddffc8409954fe60f85a':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('common_image_container' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\EvenHub\common_image_container.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':3,'path_anchored_functions':2,'body_bytes':1554,'physical_bytes':1834,'noncode_bytes':280,'reachable_instructions':591,'direct_body_calls':81,'internal_direct_body_calls':1,'external_direct_body_calls':80,'indirect_body_calls':0,'direct_bl_entry_sites':3,'stored_function_entry_pointers':0,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':70,'lvgl_calls':3,'source_owned_heap_calls':3,'source_owned_cache_calls':1,'bounded_abs_calls':1,'first_party_calls':2,'historical_container_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
