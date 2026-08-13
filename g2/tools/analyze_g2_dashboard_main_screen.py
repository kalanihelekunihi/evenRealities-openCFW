#!/usr/bin/env python3
"""Fail-closed object/provider audit for ui_DashBaord_Main_Screen.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-dashboard-main-screen-function-map.tsv";CL=ROOT/"tools/manifests/g2-dashboard-main-screen-closure.tsv";PM=ROOT/"tools/manifests/g2-dashboard-main-screen-provider-map.tsv"
PINS={FM:"47b03f0af493a07534fea5264a169141e387a5b713aafe3d78e6cee26e0f0d2b",CL:"a84ae05c0bdd15e5bd1c78844f590fd521f16a77ffd9f4b31637ee1c809ae4dd",PM:"7a8b79eadc92da68a4a1b3848fbfd7791663910e8d5d08a6b9c72fabb0bf68ec"}
PHYS=(0x4E772C,0x4E9DD4);PATH_CELLS=(0x4E7FE4,0x4E8A78,0x4E936C,0x4E9D60)
EASY={0x43CE9E,0x43D0CE,0x43D574}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6AC,0x43F6D6,0x43FCE0,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44130C,0x44131C,0x44133A,0x441378,0x441386,0x441394,0x4413A2,0x4413B0,0x44140E,0x44142E,0x44146A,0x441488,0x44DCA2,0x44E368,0x44E498,0x44EA04,0x4503D6,0x450408,0x4506CE}
CMSIS={0x4497B6,0x44981C};IAR={0x439BE4,0x439C04,0x43C0E4}
FIRST={0x45A568,0x45A570,0x464BB2,0x464C36,0x466512,0x49C5BC,0x4E75B0,0x4E75E2,0x4EB33C,0x4EB4A4,0x4EBDFC,0x4EBF5C,0x4EC2DC,0x4ED6C4,0x4ED9B6,0x4EDAC4,0x4EEADC,0x4EEBDC,0x4EF9A4,0x4EFCB8,0x4EFEB0,0x4EFFFC,0x4F091C,0x4F2CEC,0x4F2EC0,0x4F3084,0x4F3128,0x4F31C8,0x4F326C,0x4F3440,0x4F4030,0x4F4670,0x4F4ED8,0x4F6880,0x4F8644,0x4F8878,0x4F891C,0x4F8FFC,0x4FAF9C,0x4FB08C,0x4FB5E8,0x4FB760,0x4FC1DC,0x4FC360,0x4FD7B0,0x4FD840,0x4FFEB4,0x5000CC,0x5004B2,0x50060E,0x50062C,0x500646,0x50067A,0x500696,0x5006F8,0x500712,0x50072C,0x500746,0x500760,0x50077A,0x500796,0x5007B0,0x502174,0x509694,0x509C1C,0x509C96,0x509CA2,0x509DFA,0x509E14,0x509F52,0x509F7A,0x509F86,0x509F8E,0x50FEF8,0x50FF0E,0x558142,0x558314}
STORED=[(0x4E845C,0x4E78AB),(0x4E8464,0x4E7903),(0x4E8480,0x4E7A75),(0x4E848C,0x4E78A1),(0x4E8494,0x4E7803),(0x4E9384,0x4E7A05),(0x4E938C,0x4E7A11),(0x4E93B0,0x4E82A7),(0x4E93B4,0x4E832B),(0x4E9D34,0x4E82ED),(0x4E9D38,0x4E8371),(0x4E9DC0,0x4E79A9),(0x4E9DC8,0x4E79B5)]
STORED_INTERIOR=[(0x62F470,0x4E7F7F),(0x6330B5,0x4E7F7F),(0x6332C2,0x4E7F7F),(0x634FCD,0x4E7F7F),(0x634FEC,0x4E7F7F),(0x636D87,0x4E7F7F),(0x64E50A,0x4E7F9F)]
PSEUDO_WORDS=[(0x5EB041,0x4E95D3,0x4E95D0),(0x62EAAA,0x4E8FFD,0x4E8FFA),(0x6988F2,0x4E8565,0x4E8562),(0x698CF2,0x4E8565,0x4E8562),(0x699CF2,0x4E8565,0x4E8562),(0x69A0F2,0x4E8565,0x4E8562)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());kernel=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text())
 if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or kernel["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c":raise c.AuditError("RTOS changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
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
 if len(F)!=31 or sum(r['source_path_anchor']=='yes' for r in rows)!=8:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=9040 or sh(body)!="dc90a40e90703f1ba436bdbe8b0e3026ca2e1a3d8b2123d474ce01d572c4d48e" or len(ins)!=3353 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="de41ac70a646fb3979d4cae8064efa1614349282702477da71a45e8a87e9bd8e" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=856 or sh(non)!="5c08a87b4a4671836bdbf0d8c9d3c6fec00408e5b2b91cbd65b93b6e5bed3a6e" or sh(c._slice(b,*PHYS))!="ab50c77d3eefcde775887bfd963f776a2b56ae2dc1b91653d2d9a164fdff0ffd":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="bb1433f6b5578c349d4e9fe11c62d5e800f14ce75f8bbf5d346b677868d7160e" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="f1aa287d3848b4eb10793cc08b8f7d65c1730153ce098417f7588e937b2964fa":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,CMSIS,IAR,FIRST)
 if len(calls)!=542 or sum(y in starts for x,y in calls)!=23 or c._pair_digest(calls)!="65885760d91433b73841c4de3b4f1c4bb900107b0a3dfcedb70361888337aa22" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(255,146,2,7,109):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=49 or c._pair_digest(entries)!="aca2970e90943a0dd6c6f2efaaf96e1de50209cf855a166852243ce39b3bf045" or strict:raise c.AuditError("BL ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 if [(a,v) for a,v in words if v in enc]!=STORED:raise c.AuditError("stored function entries changed")
 if [(a,v) for a,v in words if (v&1) and (v&~1) in inter]!=sorted(STORED_INTERIOR+[(a,v) for a,v,cover in PSEUDO_WORDS]):raise c.AuditError("stored interior word census changed")
 if any((v&~1) not in ins for a,v in STORED_INTERIOR):raise c.AuditError("interior callback target is not decoded")
 if any(cover not in ins or ins[cover].size!=4 or (v&~1)!=cover+2 for a,v,cover in PSEUDO_WORDS):raise c.AuditError("pseudo-pointer overlap proof changed")
 if cstring(b,0x6E1D2C)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=52 or c._pair_digest(pairs)!="13b7fe6b6cccf2480fac0ce11ddbc3e1e0a950746c1d5876cf44286e743304fe":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("ui_dashboard_main_screen" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":31,"ghidra_discovered_functions":14,"restored_functions":17,"path_anchored_functions":8,"body_bytes":9040,"physical_bytes":9896,"noncode_bytes":856,"reachable_instructions":3353,"direct_body_calls":542,"internal_direct_body_calls":23,"external_direct_body_calls":519,"indirect_body_calls":0,"direct_bl_entry_sites":49,"stored_function_entry_pointers":13,"stored_interior_callback_pointers":7,"unaligned_word_pseudo_pointers":6,"strict_interior_bl_ingress":0},"behavior":{"main_dashboard_screen_construction":True,"watchface_widget_composition":True,"input_and_animation_callbacks":True,"dashboard_data_and_resource_dispatch":True,"role_and_display_policy":True},"provider_boundary":{"easylogger_calls":255,"lvgl_calls":146,"cmsis_freertos_calls":2,"iar_dlib_calls":7,"first_party_calls":109,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
