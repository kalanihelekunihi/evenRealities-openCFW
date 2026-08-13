#!/usr/bin/env python3
"""Fail-closed object/provider audit for MessageNotify/ui_msg_notif_list.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-ui-msg-notif-list-function-map.tsv";CL=ROOT/"tools/manifests/g2-ui-msg-notif-list-closure.tsv";PM=ROOT/"tools/manifests/g2-ui-msg-notif-list-provider-map.tsv"
PINS={FM:"67d9541d516f3a31a38e0608874acc8c4d7c9402f0eac2b748b76cbc066b3b63",CL:"d29ef7318a85fb4f7dcba61e401429d81d644be573f1dc02a5bfe1283ad92058",PM:"61410750111fe22ff22beeadfed2215cb572b2d89fab4d45037765e035431b7b"}
PHYS=(0x54FF36,0x552CDC);PATH_CELLS=(0x550954,0x55148C,0x552218,0x55288C)
EASY={0x43CE9E,0x43D0CE,0x43D574}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E0E0,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6B8,0x43F6D6,0x43FCE0,0x43FD9E,0x43FDDA,0x44104C,0x4411AA,0x44120E,0x441238,0x44127E,0x44129E,0x4412EC,0x44130C,0x44131C,0x44133A,0x441348,0x441368,0x441378,0x44140E,0x44143E,0x44145A,0x44146A,0x441488,0x44D7B8,0x44DCE2,0x44E368,0x44E3CA,0x44E498,0x44EA04,0x4503D6,0x450408,0x4506CE,0x498668,0x498680,0x499416,0x49942E,0x499678,0x4997F8}
CMSIS={0x4490CC,0x44971C,0x44986E};IAR={0x43C0E4,0x44A43C,0x46CACC,0x48D540};HEAP={0x474CD2,0x474D16}
FIRST={0x443484,0x4434D0,0x45A568,0x45FFFE,0x460084,0x464BB2,0x464C36,0x49729C,0x4974D4,0x49758E,0x497826,0x509694,0x509C1C,0x509C96,0x509DFA,0x509E14,0x50FEF8,0x50FF0E,0x54FA24,0x54FB84,0x552D40,0x552D74,0x552DB2,0x552DF0,0x5532F8,0x553338,0x5533CC,0x567C80,0x588550,0x588598}
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
 if len(F)!=50 or sum(r['source_path_anchor']=='yes' for r in rows)!=18:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=10808 or sh(body)!="5bd26bcca6f43da36d43d6c9cce57c50a8e828b2c99a5d44642e481dfb9fb550" or len(ins)!=4221 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="5019c85bbe674bb3dc4051af7b25f98751745b4c492babad836d827f59bc3b1d" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=878 or sh(non)!="5d2486380d85f252e3742c14e519e36b8d82164ddb57bf2af9810c09ca329779" or sh(c._slice(b,*PHYS))!="0dee81bf69e5545a9790d95c5cc09ddfd2eba920f3bff9fa746f58e535b9959a":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="0b9deeb42ab312e5c9a41a9fc561c58cbeb9645d767f161c4d60a9a8b39f46d7" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="da3c44c5b2e4869e1468f03290fe0a8bfae4e873358daefc9ca4a76f05b7e524":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,CMSIS,IAR,HEAP,FIRST)
 if len(calls)!=661 or sum(y in starts for x,y in calls)!=62 or c._pair_digest(calls)!="2d6ac13e5beb5845945cf4b34244d388636075bbf08919548366fa879f9e9781" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(205,304,6,11,8,65):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=93 or c._pair_digest(entries)!="cc8d189cb31bd4ee987f38c1d0a7d9b8514e5e7f99ca10960cfe037ebae11490" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x4F8803,0x552820),(0x5512AC,0x5505EB),(0x55130C,0x550433),(0x5ECCA9,0x552820)]:raise c.AuditError("stored entries changed")
 if cstring(b,0x6F0AD8)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\MessageNotify\ui_msg_notif_list.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=35 or c._pair_digest(pairs)!="c4611939bce64a2a3b7c13ef210afc0d7c6e5ca190ec9681e69b82a827d23f11":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("ui_msg_notif_list" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\MessageNotify\ui_msg_notif_list.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":50,"ghidra_discovered_functions":37,"restored_functions":13,"path_anchored_functions":18,"body_bytes":10808,"physical_bytes":11686,"noncode_bytes":878,"reachable_instructions":4221,"direct_body_calls":661,"internal_direct_body_calls":62,"external_direct_body_calls":599,"indirect_body_calls":0,"direct_bl_entry_sites":93,"stored_entry_pointers":4,"strict_interior_ingress":0},"behavior":{"notification_list_construction_and_layout":True,"ancc_count_and_record_access":True,"message_time_and_resource_formatting":True,"selection_scroll_and_navigation":True,"bounded_string_and_item_helpers":True},"provider_boundary":{"easylogger_calls":205,"lvgl_calls":304,"cmsis_freertos_calls":6,"iar_dlib_calls":11,"source_owned_heap_wrapper_calls":8,"first_party_calls":65,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","tlsf_commit":"deff9ab509341f264addbd3c8ada533678591905","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
