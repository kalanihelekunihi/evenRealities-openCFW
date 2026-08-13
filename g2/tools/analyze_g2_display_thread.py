#!/usr/bin/env python3
"""Fail-closed object/provider audit for framework/sync/display_thread.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-display-thread-function-map.tsv";CL=ROOT/"tools/manifests/g2-display-thread-closure.tsv";PM=ROOT/"tools/manifests/g2-display-thread-provider-map.tsv"
PINS={FM:"31ad6a4fe7f759f0f3a6d01d39b77ca4fd1ae76a4172ffb1732f089fad578c4b",CL:"b3758c5cc0cec0dc005f57efab7710565a2779fb57b7c21da03c7118cdaf5d41",PM:"a2a7cc6679615b524740d7f3f33376aa5f2e58d1963ae873aa856b3622ac7571"}
PHYS=(0x44228A,0x4448F4);PATH_CELLS=(0x442CF0,0x44375C,0x4443A8,0x444898)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490E2,0x44971C,0x4497B6,0x44981C,0x449A32,0x449ABE,0x449B3C};FREERTOS={0x454B4C,0x5FA0A4};LVGL={0x464344};IAR={0x439BE4,0x439C04,0x43C0E4};RUNTIME={0x4733EE}
FIRST={0x442238,0x442256,0x44227E,0x44D254,0x44FF38,0x45A568,0x45A8EE,0x45BBF4,0x45F15A,0x45F3C8,0x45F6A8,0x45F706,0x45F7BE,0x45F840,0x45F876,0x45F8D0,0x45F8E6,0x45F8FC,0x45FAA8,0x45FE32,0x45FFFE,0x460084,0x460090,0x4600B4,0x460106,0x460374,0x4628C4,0x464242,0x464B2E,0x464C36,0x465B10,0x465D7C,0x46651E,0x467F08,0x468034,0x469AE2,0x46AE9C,0x46BE7C,0x46C01C,0x46C0E8,0x46C600,0x46C622,0x46C984,0x46C9AA,0x46CACC,0x46D464,0x46D816,0x46D826,0x46D8A0,0x46D8C4,0x46D9AC,0x46F32C,0x46F68A,0x46F6A2,0x471164,0x471C9A,0x471CAE,0x471CD6,0x471D58,0x471DAC,0x471E92,0x471E9E,0x471EBC,0x471FA4,0x47243A,0x473474,0x473548,0x473928,0x473934,0x47394C}
EXPECTED_IND=[0x4422E8,0x44232A,0x442374,0x442500,0x44255A,0x4438E4,0x4438EA,0x4439C0,0x4439C6,0x443E0C,0x443E12,0x44468C]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
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
 if len(F)!=27 or sum(r['source_path_anchor']=='yes' for r in rows)!=14:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if len(body)!=9100 or sh(body)!="a6e8474e75e12304f39294cf793c131b219219653291aa87a6d2ba6d4441aeca" or len(ins)!=3370 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="435a7bccf13c2aa55c3eaa0f67fcfa0044ff27473a4c41e7bbcccdef4650a14d" or ind!=EXPECTED_IND:raise c.AuditError("instruction closure changed")
 mask=bytearray(PHYS[1]-PHYS[0])
 for a,i in ins.items():
  for j in range(i.size):mask[a-PHYS[0]+j]=1
 rawphys=c._slice(b,*PHYS);non=bytes(v for v,m in zip(rawphys,mask) if not m)
 if len(non)!=734 or sh(non)!="7c83acb922cf34e4025b894dad4a114dd9919f31b5d7e875d090297709c2e075" or sh(rawphys)!="e0b5514252793850b22b4a49f5419301d03498bf78b4c07608af63d0fa3c8ba9":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="d1aea8160b12f98310f08af3461661907547bc33916465954ad7b7e3826b5700" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="fa56563071f7b2efc0c0e724ad2eecfb698ff6cfe7769921923a660118527a4f":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS,LVGL,IAR,RUNTIME,FIRST)
 if len(calls)!=545 or sum(y in starts for x,y in calls)!=23 or c._pair_digest(calls)!="41e3b1051dfcf70231dba3ca3dc9855c1da309bfe317c88d992b6f49fdfa4f69" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(310,21,11,12,23,5,140):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=201 or c._pair_digest(entries)!="7841508b70353906fa7336e297ee76067452a93907604c108fb4121de9eaa0b2" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x43814C,0x44466D),(0x4448BC,0x444685),(0x4448F0,0x4437E1)]:raise c.AuditError("stored entries changed")
 if cstring(b,0x701FB4)!=r"D:\01_workspace\s200_ap510b_iar_git\framework\sync\display_thread.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=62 or c._pair_digest(pairs)!="befd5f00fc9a534e5a8f8f058ab02514eb23c9d5de6b845abee9f9a5a7c09b1c":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 sources=[x for x in overlay['sources'] if x.get("path","").lower().endswith("ui_display_thread.c")]
 patches={x.get("name"):(x.get("runtime_address"),x.get("target_function")) for x in overlay['patch_sites']}
 if len(sources)!=1 or patches.get("replace_ui_display_thread")!=(0x4437E0,"open_cfw_ui_display_thread") or patches.get("replace_ui_display_callback")!=(0x444684,"open_cfw_ui_display_callback"):raise c.AuditError("production routing changed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"framework\sync\display_thread.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":27,"ghidra_discovered_functions":14,"restored_functions":13,"path_anchored_functions":14,"body_bytes":9100,"physical_bytes":9834,"noncode_bytes":734,"reachable_instructions":3370,"direct_body_calls":545,"internal_direct_body_calls":23,"external_direct_body_calls":522,"indirect_body_calls":12,"direct_bl_entry_sites":201,"stored_entry_pointers":3,"strict_interior_ingress":0},"behavior":{"display_thread_lifecycle":True,"page_and_animation_dispatch":True,"lvgl_timer_pump":True,"cmsis_queue_and_mutex_use":True,"bounded_callback_dispatch":True},"provider_boundary":{"easylogger_calls":310,"cmsis_freertos_calls":21,"freertos_calls":11,"lvgl_calls":12,"iar_dlib_calls":23,"source_owned_runtime_calls":5,"first_party_calls":140,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":True,"source_routed_functions":2}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
