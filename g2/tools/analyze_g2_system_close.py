#!/usr/bin/env python3
"""Fail-closed stock/provider audit for SystemClose/systemClose.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-system-close-function-map.tsv';PM=ROOT/'tools/manifests/g2-system-close-provider-map.tsv';CL=ROOT/'tools/manifests/g2-system-close-closure.tsv'
PINS={FM:'367d349f69f33c0d3bbc9c8a72548b63dcf0648df1d2e3491a70b53eb68f47e1',PM:'7d2d13107465ee484fdca0d63434257c2f6d8533f534ff0fc2d959e8e847bfed',CL:'44a30bddacb4d5da36cd140ecd55c038b4a3914ba3155bebd688a22ef4e30ef3'}
F=((0x469BF4,0x469C26),(0x469C26,0x469C98),(0x469C98,0x469CAC),(0x469CAC,0x469D24),(0x469D24,0x469D48),(0x469D48,0x469E66),(0x469E66,0x469FA2),(0x469FA2,0x46A18C),(0x46A18C,0x46A2CA),(0x46A2CA,0x46A3D6),(0x46A3D8,0x46A4E2),(0x46A4E2,0x46A53A),(0x46A53A,0x46A6D2),(0x46A6D2,0x46A77E),(0x46A77E,0x46A822),(0x46A848,0x46AAB6),(0x46AAE8,0x46ACC4),(0x46ACE8,0x46AE6A),(0x46AE9C,0x46AEEA),(0x46AEEA,0x46B004))
G=((0x46A3D6,0x46A3D8),(0x46A822,0x46A848),(0x46AAB6,0x46AAE8),(0x46ACC4,0x46ACE8),(0x46AE6A,0x46AE9C),(0x46B004,0x46B0EC));PHYS=(0x469BF4,0x46B0EC);PATH=0x6FD8A4;CELLS=(0x46A830,0x46B054)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6B8,0x43FC70,0x43FCE0,0x43FD9E,0x43FDDA,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44140E,0x44143E,0x44146A,0x44D878,0x44DCA2,0x44E368,0x44E3CA,0x4503D6,0x450408,0x450500,0x4506CE,0x498668,0x498680,0x499416,0x49942E}
FIRST={0x443484,0x443504,0x45A568,0x45A8EE,0x45ACCC,0x45FFFE,0x460084,0x464BB2,0x464C36,0x464D1C}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());lv=json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or lv['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('provider provenance changed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if tuple((int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows)!=F or len(rows)!=20 or sum(r['source_path_anchor']=='yes' for r in rows)!=10 or sum(r['ghidra_discovered']=='yes' for r in rows)!=5:raise c.AuditError('function inventory changed')
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB);starts={a for a,_ in F};inter=set();ins=[];calls=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii=list(md.disasm(raw,a))
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or sum(x.size for x in ii)!=len(raw):raise c.AuditError('linear instruction body changed')
  body+=raw;ins += [(x.address,x.size) for x in ii];inter.update(range(a+2,z,2))
  for x in ii:
   y=t._thumb_bl_target(b,x.address)
   if y is not None:calls.append((x.address,y))
   if x.mnemonic=='blx' and not x.op_str.startswith('#'):raise c.AuditError('indirect body call appeared')
 calls.sort()
 if len(body)!=4960 or sh(body)!='74b212134204b68879b99cb2d9f1a79da09749afa99812c42574b30c83a2e12c' or len(ins)!=1854 or c._instruction_digest(ins)!='264b7c598a5cd180d2fb3d40f97c7a45b6a944033e045d9321bee49308eef4e9':raise c.AuditError('instruction closure changed')
 gaps=b''.join(c._slice(b,a,z) for a,z in G)
 if len(gaps)!=408 or sh(gaps)!='e7b2b41924f479da4b2f9c876aa3df78494eebd31c3994003823e6e1dd69813f' or sh(c._slice(b,*PHYS))!='5556495cafcc9fcc4adb676d16c9cb5a6150010b6015285d5b476964d810ee0e':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,0x469BE4,0x469BF4))!='d4506d9a3160cfc88970ede63e91bd74553bd6dc2447951285debc02345ba506' or sh(c._slice(b,0x46B0EC,0x46B0FC))!='fbb1c11b609f2e745f8c8385b460b6ca2cbe45573581ce2c3d9d247a43c95994':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,LVGL,IAR,FIRST)
 if len(calls)!=296 or sum(y in starts for _,y in calls)!=25 or c._pair_digest(calls)!='e62f1f02099673182633c1c96e04819d67eef0b23fce0138f27f4dec203f5292' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(130,99,5,37):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non.append((a,y))
 if len(entries)!=40 or c._pair_digest(entries)!='5862d5efd1c901cd131975ed913d223df6e4f74c60ed6f59635372dde92f14da' or strict or non:raise c.AuditError('BL ingress changed')
 stored=[];raw=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0];y=v&~1
  if y in starts or y in inter:raw.append((c.BASE+off,v,y))
  if v&1 and y in starts:stored.append((c.BASE+off,y))
 expected_stored=[(0x46AE90,0x46A3D8),(0x6A4694,0x469D48),(0x6A4698,0x46AEEA)]
 if stored!=expected_stored or len(raw)!=11:raise c.AuditError('raw pointer topology changed')
 if c._slice(b,PATH,b.find(b'\0',PATH-c.BASE)+c.BASE).decode('ascii')!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\SystemClose\systemClose.c':raise c.AuditError('retained path changed')
 refs=[]
 for cell in CELLS:
  if struct.unpack('<I',c._slice(b,cell,cell+4))[0]!=PATH:raise c.AuditError('path cell changed')
  refs += [(cell,x) for x in t.literal_references(b,cell)]
 body_refs=[x for _,x in refs if any(a<=x<z for a,z in F)]
 if len(refs)!=27 or refs[-1]!=(0x46B054,0x46B010) or len(body_refs)!=26 or len({next(a for a,z in F if a<=x<z) for x in body_refs})!=10 or c._pair_digest(refs)!='9b2067b1c57b6c0fac63bb0b3dd54d406ffa27464da1d691d28cfafa6b759c02':raise c.AuditError('path references changed')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\SystemClose\systemClose.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':20,'ghidra_discovered_functions':5,'restored_functions':15,'path_anchored_functions':10,'raw_path_references':27,'raw_path_referencing_functions':10,'body_bytes':4960,'physical_bytes':5368,'noncode_bytes':408,'reachable_instructions':1854,'direct_body_calls':296,'internal_direct_body_calls':25,'external_direct_body_calls':271,'indirect_body_calls':0,'direct_bl_entry_sites':40,'stored_entry_pointers':3,'raw_interior_word_collisions':8,'strict_interior_ingress':0},'behavior':{'bounded_event_fifo':True,'common_data_gate':True,'scroll_selection':True,'confirm_cancel_minimize':True,'imu_reflash_dispatch':True,'display_lifecycle':True},'provider_boundary':{'easylogger_calls':130,'lvgl_calls':99,'iar_dlib_calls':5,'first_party_calls':37,'direct_cmsis_freertos_calls':0,'easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','historical_system_close_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
