#!/usr/bin/env python3
"""Fail-closed object/provider audit for EvenHub evenhub_data_parser.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-evenhub-data-parser-function-map.tsv";CL=ROOT/"tools/manifests/g2-evenhub-data-parser-closure.tsv";PM=ROOT/"tools/manifests/g2-evenhub-data-parser-provider-map.tsv"
PINS={FM:"35f5471c93e4fa1ad9f341e4e6a7c436984f826e493a9dbc96f9957aa613bbde",CL:"f61be1d1cd32950ed1f33bd104a9cbda8791e302a55d485eb26d95c178387751",PM:"8639d182327120e8201ef1c973f755c498a66bb1d4aa5fab0498d9b2b4e510b9"}
PHYS=(0x4D9B34,0x4DC5AE);PATH_CELLS=(0x4DA5FC,0x4DA814,0x4DB4C0,0x4DBE30)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4,0x44A43C,0x44B5A0};CMSIS={0x44971C,0x4497B6,0x44981C};HEAP={0x474CD2,0x474D16};NANOPB={0x48EB32,0x48F49C,0x490120,0x4905F4,0x490C32}
LVGL={0x43DE82,0x43F09A,0x43F4C0,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44146A,0x44D7B8,0x498668}
FIRST={0x4434D0,0x45A568,0x45A570,0x45AACA,0x464B2E,0x464BB2,0x464F76,0x475B14,0x475C1A,0x4A6D58,0x4A6DCA,0x4A6E3C,0x4DCC80,0x4E0CCE}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
 if json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
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
 if len(F)!=19 or sum(r['source_path_anchor']=='yes' for r in rows)!=12:raise c.AuditError("inventory changed")
 starts={a for a,z in F};ins={};calls=[];ind=[];interval=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("function interval changed")
  ins.update(ii);calls+=cc;ind+=dd;interval+=raw
 calls.sort();ind.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(interval)!=10496 or sh(interval)!="f89303aa9c3921697daa89ab0a0ed7a0c6f34b90999c0e7b4e3ca2a2dddc8181" or len(code)!=10336 or sh(code)!="001e3cb7815ced88c2587557bd0e640693900aca25266bb3a9134754ef712c05" or len(ins)!=3819 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="97bb5b6f92b8d694e1e0dd982e3032e6c4511c76505d18891f70d57bf0d82823" or ind:raise c.AuditError("instruction closure changed")
 mask=bytearray(PHYS[1]-PHYS[0])
 for a,i in ins.items():
  for j in range(i.size):mask[a-PHYS[0]+j]=1
 rawphys=c._slice(b,*PHYS);non=bytes(v for v,m in zip(rawphys,mask) if not m)
 if len(non)!=538 or sh(non)!="82e62db1be34bd4bcd134da96b7d0f380d3ce1826c2e9a7c779a8da756954e7a" or sh(rawphys)!="a0229735100064adb46bb5125c9ec7642b32826ac2f4b398986b0c53e75f622e":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="19d9334002430b93ef4578c3ea1af5db1aeab0a0fa6fc2fca4aa16ecd864b124" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="b51dc6f0e7383fb0756ab2d2e81fbc6b712eb5ac400154e4dedacde40254c245":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,NANOPB,CMSIS,LVGL,IAR,HEAP,FIRST)
 if len(calls)!=590 or sum(y in starts for x,y in calls)!=49 or c._pair_digest(calls)!="0e683e8de12559928782895a4cb73efff0300154fefadbd725ba7a158b1d1517" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(385,25,3,14,54,12,48):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in ins:strict.append((a,y))
 if len(entries)!=93 or c._pair_digest(entries)!="bb0ab23d895696722b86879ff1fb24987f15e16bb5bd2f133a147b843a8e91c6" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored:raise c.AuditError("stored entries changed")
 if cstring(b,0x6F3434)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_data_parser.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=63 or c._pair_digest(pairs)!="a08eabd6eb8b893d1ae35ecdd5f31290c3683e2faddc8030beed2fe853fb77ee":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("evenhub_data_parser" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\EvenHub\evenhub_data_parser.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":19,"ghidra_discovered_functions":17,"restored_functions":2,"path_anchored_functions":12,"function_interval_bytes":10496,"body_bytes":10336,"physical_bytes":10874,"noncode_bytes":538,"reachable_instructions":3819,"direct_body_calls":590,"internal_direct_body_calls":49,"external_direct_body_calls":541,"indirect_body_calls":0,"direct_bl_entry_sites":93,"stored_entry_pointers":0,"strict_interior_ingress":0},"behavior":{"protobuf_decode_encode":True,"schema_dispatch":True,"container_construction":True,"role_and_display_policy":True,"inline_table_islands_bounded":True},"provider_boundary":{"easylogger_calls":385,"nanopb_calls":25,"cmsis_freertos_calls":3,"lvgl_calls":14,"iar_dlib_calls":54,"source_owned_heap_wrapper_calls":12,"first_party_calls":48,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
