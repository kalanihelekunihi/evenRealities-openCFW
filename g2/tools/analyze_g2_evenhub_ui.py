#!/usr/bin/env python3
"""Fail-closed object/provider audit for EvenHub evenhub_ui.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-evenhub-ui-function-map.tsv";CL=ROOT/"tools/manifests/g2-evenhub-ui-closure.tsv";PM=ROOT/"tools/manifests/g2-evenhub-ui-provider-map.tsv"
PINS={FM:"4cc6d816f778188d6285a87067d98e45fa2ed2d4adb5c31a771c0498c776c721",CL:"27ac8fe0c188023c1ea32fd90a6fd3340f7e3626efcb6305f26fc83301736d93",PM:"9933bb0c3cc5fd3e566fadf28a126ecb72e41f41343c16cb1f90dc01eecaf105"}
PHYS=(0x4935CC,0x49729C);PATH_CELLS=(0x4940BC,0x49447C,0x494B80,0x4954F4,0x4961A0,0x49651C,0x497194)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4,0x44B5A0};HEAP={0x474CD2,0x474D16};NANOPB={0x48EB32,0x48F49C,0x490120};LZ4={0x4E0C0C,0x4E0C34}
LVGL={0x43DE82,0x43DFA4,0x43F09A,0x43F506,0x43F568,0x43F6AC,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44133A,0x441378,0x441386,0x4413B0,0x44140E,0x44142E,0x44143E,0x44146A,0x44D878,0x499416,0x49942E}
FIRST={0x45A568,0x45A570,0x45FFFE,0x460084,0x4641B6,0x464C36,0x465480,0x46AE9C,0x4D9BFE,0x4D9C86,0x4DA16A,0x4DA382,0x4DA56E,0x4DBEDE,0x4DC5AE,0x4DCA3C,0x4DD510,0x4DE17C,0x4DE354,0x4DEE96,0x4DF6EE,0x4E033C,0x4E0CA0,0x4E0CB2,0x4E0CBA,0x4E0CC4,0x4E1406}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
 if json.loads((ROOT/"third_party/lz4/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="ebb370ca83af193212df4dcbadcc5d87bc0de2f0":raise c.AuditError("LZ4 changed")
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
 if len(F)!=26 or sum(r['source_path_anchor']=='yes' for r in rows)!=21:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=14296 or sh(body)!="6835e5af515f00bff0f6dc90fc3055567ac1e7df798e6d0cec2e20b6b86c426a" or len(ins)!=5159 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="5ad50760bde0401e53f63bf751263da04f3293c21dadb3b3cf5c2e6e59f5964a" or ind!=[0x493F54,0x4947D0]:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=1272 or sh(non)!="3d06a13b9ca9c8c7363d4414ed572edf85ce20b7e31774602d1ef7ce5938d209" or sh(c._slice(b,*PHYS))!="a23b04619a8ee465cb2fda5dbedebc27ac0a03f214235945099021543ed13e30":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="28d0ce74e1fc0b1335a885ef7ce57d9b6c76672dcb87c8d8600c2a62597e80b1" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="97209633f070886ee767b08453b73bb1e87ad91a451bb10588e776717f69fe80":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,NANOPB,IAR,HEAP,LZ4,FIRST)
 if len(calls)!=855 or sum(y in starts for x,y in calls)!=32 or c._pair_digest(calls)!="ba2c29315253571d047f2f0f39bcb1d02c6fafc6847b1227d78541229b93b0e3" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(690,37,7,22,10,2,55):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=44 or c._pair_digest(entries)!="527e8bd6f4662a18693082d9da676b33fc9a7d0999ed5aa3868640a1ff4400e0" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 expected=[(0x495548,0x4940E9),(0x49556C,0x4949C1),(0x495578,0x495F9B),(0x49559C,0x494A79),(0x4955A8,0x4961E5),(0x4961D4,0x4940E9),(0x4963FC,0x4949C1),(0x496408,0x495F9B),(0x49642C,0x494A79),(0x4964D4,0x4961E5)]
 if stored!=expected:raise c.AuditError("stored entries changed")
 if [x for x in entries if x[1]==0x493EE6]!=[(0x494EEA,0x493EE6),(0x495852,0x493EE6)] or [x for x in entries if x[1]==0x4942A4]!=[(0x4950EC,0x4942A4),(0x4952C2,0x4942A4),(0x495A54,0x4942A4),(0x495C3A,0x4942A4)]:raise c.AuditError("callback caller closure changed")
 if cstring(b,0x702A54)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_ui.c":raise c.AuditError("path changed")
 path_pairs=[(cell,ref) for cell in PATH_CELLS for ref in t.literal_references(b,cell)]
 if len(path_pairs)!=138 or c._pair_digest(path_pairs)!="0e02f37613a64b735c2024a13828191191c788ea343cbda85ba937ac05fb8292":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().endswith("evenhub_ui.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\EvenHub\evenhub_ui.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":26,"ghidra_discovered_functions":10,"restored_functions":16,"path_anchored_functions":21,"body_bytes":14296,"physical_bytes":15568,"noncode_bytes":1272,"reachable_instructions":5159,"direct_body_calls":855,"internal_direct_body_calls":32,"external_direct_body_calls":823,"indirect_body_calls":2,"bounded_indirect_targets":3,"direct_bl_entry_sites":44,"stored_entry_pointers":10,"strict_interior_ingress":0},"behavior":{"container_lifecycle":True,"side_specific_page_construction":True,"protobuf_decode_encode":True,"event_injection":True,"bounded_internal_callbacks":True},"provider_boundary":{"easylogger_calls":690,"lvgl_calls":37,"nanopb_calls":7,"iar_dlib_calls":22,"source_owned_heap_wrapper_calls":10,"closed_lz4_adapter_calls":2,"first_party_calls":55,"indirect_callback_sites":2,"bounded_indirect_targets":3,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","lz4_commit":"ebb370ca83af193212df4dcbadcc5d87bc0de2f0","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
