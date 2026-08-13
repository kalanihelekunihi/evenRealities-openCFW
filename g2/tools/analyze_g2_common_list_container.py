#!/usr/bin/env python3
"""Fail-closed object/provider audit for EvenHub common_list_container.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-common-list-container-function-map.tsv";CL=ROOT/"tools/manifests/g2-common-list-container-closure.tsv";PM=ROOT/"tools/manifests/g2-common-list-container-provider-map.tsv"
PINS={FM:"196e8f1dc73ce25d34e6071afbb1d3866fb2e729f445e94eed94031b874e50a1",CL:"47cee7835d3b5cf3c25acdaf0ada292a880b493f994bbcda86ad38e3daa6b908",PM:"d5e198ce1c5f9b7d63bb03f6406e2e51a7e3ea9403d31fceba76dbccffe0a882"}
PHYS=(0x4DCCD8,0x4DEE64);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439C04,0x43C0E4,0x44B5A0};HEAP={0x474CD2,0x474D16};FIRST={0x509C1C,0x509C96,0x509CA2,0x509DFA,0x509E14,0x509F52}
LVGL={0x43DE82,0x43DFA4,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43FCE0,0x4409FA,0x44104C,0x441180,0x4411AA,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44140E,0x44143E,0x44146A,0x441488,0x44D7B8,0x44DCE2,0x44E368,0x44E3CA,0x44E498,0x44EA04,0x4503D6,0x450408,0x4506CE,0x499416,0x49942E,0x499678}
PATH_CELLS={0x4DD470:[0x4DCD5C,0x4DCEEE,0x4DCF4A,0x4DCFA8,0x4DD078,0x4DD0D0,0x4DD130,0x4DD18C,0x4DD200,0x4DD252,0x4DD29A,0x4DD33A,0x4DD386,0x4DD3DA],0x4DE150:[0x4DD544,0x4DD5A6,0x4DD610,0x4DD66A,0x4DD6C0,0x4DD716,0x4DD76C,0x4DD7C0,0x4DD814,0x4DD868,0x4DD8C4,0x4DD92A,0x4DD990,0x4DDA62,0x4DDAC2,0x4DDB10,0x4DDB62,0x4DDC2A,0x4DDCC4,0x4DDD24,0x4DDD98,0x4DDDEE,0x4DDE8E,0x4DE012,0x4DE0BA,0x4DE104],0x4DE344:[0x4DE198,0x4DE1D8,0x4DE262],0x4DEDD8:[0x4DE37A,0x4DE3D2,0x4DE43C,0x4DE498,0x4DE4F4,0x4DE550,0x4DE5CC,0x4DE626,0x4DE694,0x4DE6EE,0x4DE750,0x4DE7C6,0x4DE848,0x4DE8AA,0x4DE934,0x4DE9A2,0x4DEA0C,0x4DEA66,0x4DEAD0,0x4DEB2A,0x4DEBB8,0x4DEC1C,0x4DEC7C,0x4DECCC,0x4DED24,0x4DED90]}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if "deff9ab509341f264addbd3c8ada533678591905" not in (ROOT/"third_party/tlsf/README.openCFW.md").read_text():raise c.AuditError("TLSF changed")
 iar=(ROOT/"docs/research/iar-dlib-runtime-census.md").read_text()
 if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:raise c.AuditError("IAR changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=14 or sum(r['source_path_anchor']=='yes' for r in rows)!=6:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=7342 or sh(body)!="daef641f685419e53b3e9a11fdbfc258f4321985ec44dbe850a1ea36c450231c" or len(ins)!=2710 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="2db47555607309f8c13eabbbe7b2e9f3e4172c8709880e5134899fc570001ee3" or ind!=[0x4DE7A4,0x4DED72]:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=1246 or sh(non)!="90f10a1c368571877a8261d9c4e468238fbf9ffe83ca4df78229af69a0e526f1" or sh(c._slice(b,*PHYS))!="6b690c5014e1a9334adf248c6d0c92def4a2cbc598945202b8895347a62d0cea":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,0x4DCCC8,PHYS[0]))!="0f5634dd6b83d2224a3d433ec5ca5e9245e0322fdb41c56fbda94e5b87585615" or sh(c._slice(b,PHYS[1],0x4DEE74))!="33465b3e8d295c2db071c4c4df4c99a64a05151970f529fb8eab87905e4bc850":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,HEAP,FIRST)
 if len(calls)!=458 or sum(y in starts for x,y in calls)!=39 or c._pair_digest(calls)!="42447595f682972b482b5bc6503cd8575f4dd278cb1b0473c106f70bee1a7fbd" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(310,91,3,6,9):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=46 or c._pair_digest(entries)!="795e008a28e59489bf865fbfdde1112428877ce258e85a2024463ebeeb8ebcb1" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x4DD49C,0x4DCEC9),(0x4DE144,0x4DD321)]:raise c.AuditError("stored entries changed")
 constructors=[x for x in entries if x[1]==0x4DD510]
 if constructors!=[(0x49506E,0x4DD510),(0x4959D6,0x4DD510)] or struct.unpack_from('<I',b,0x49556C-c.BASE)[0]!=0x4949C1 or struct.unpack_from('<I',b,0x4963FC-c.BASE)[0]!=0x4949C1:raise c.AuditError("callback constructor closure changed")
 cb,cc,ci=q._recover_function(b,0x4949C0,0x494A72)
 if len(cb)!=67 or ci or sh(c._slice(b,0x4949C0,0x494A72))!="38371d4ccb4574a3b116288bed036975cbfd5988ceac671ad1cf128926b80931" or c._instruction_digest(sorted((a,i.size) for a,i in cb.items()))!="f6081f516a7b1b638be07c8919eee71443dbca1a2c285fb4274c9362db878a8f" or c._pair_digest(sorted(cc))!="8c9694ffd0ccceb8dc2016d5e886ecb4e8dc46a4f7bed3df576175bf7c22c8cb":raise c.AuditError("callback body changed")
 if cstring(b,0x6F1FB8)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_list_container.c":raise c.AuditError("path changed")
 for cell,refs in PATH_CELLS.items():
  if t.literal_references(b,cell)!=refs:raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("common_list_container" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\EvenHub\common_list_container.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":14,"path_anchored_functions":6,"body_bytes":7342,"physical_bytes":8588,"noncode_bytes":1246,"reachable_instructions":2710,"direct_body_calls":458,"internal_direct_body_calls":39,"external_direct_body_calls":419,"indirect_body_calls":2,"bounded_indirect_targets":1,"direct_bl_entry_sites":46,"stored_entry_pointers":2,"strict_interior_ingress":0},"behavior":{"list_object_construction":True,"row_style_and_selection":True,"queue_driven_navigation":True,"scroll_animation":True,"bounded_selection_callback":True},"provider_boundary":{"easylogger_calls":310,"lvgl_calls":91,"iar_dlib_calls":3,"source_owned_heap_wrapper_calls":6,"first_party_calls":9,"selection_callback_calls":2,"selection_callback_target":"0x004949C0","lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
