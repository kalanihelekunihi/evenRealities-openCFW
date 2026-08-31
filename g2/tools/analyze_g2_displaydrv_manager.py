#!/usr/bin/env python3
"""Fail-closed object/provider audit for displaydrv_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-displaydrv-manager-function-map.tsv";CL=ROOT/"tools/manifests/g2-displaydrv-manager-closure.tsv";PM=ROOT/"tools/manifests/g2-displaydrv-manager-provider-map.tsv"
PINS={FM:"091708f94cc20cdfb5a31cf2bab9b0bcbcb17d51cecdcbc93ba55d5139f2635b",CL:"494e3753c83ce1bd4c79f693c67241a7c0d38bdf225b9375dbcf53af6d662dc1",PM:"dfb4e671baf83a749d8f267c52698d939f8ee0eb66a0468986c4e2efa86ed95c"}
PHYS=(0x473952,0x474550);PATH_CELLS=(0x474308,0x474534);PSEUDO=(0x581EA6,0x4744AE,0x581EA4)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490E2,0x4491FE,0x4493B0,0x449498,0x4494D8,0x449A32,0x449ABE,0x449B3C};IAR={0x43C0E4}
FIRST={0x443484,0x46B238,0x46C410,0x46CA14,0x46D816,0x46D826,0x47386A,0x4C9B86,0x4C9BE2,0x4C9F32,0x4C9FB4,0x4CA010,0x4CA126,0x4CA18A,0x4CA1EE,0x4CA564,0x4CA5BE,0x4CA60E}
STORED=[(0x776A40,0x473E2F),(0x776A44,0x473EA1),(0x776A48,0x473F13),(0x776A4C,0x473F85),(0x776A50,0x473FF7),(0x791BF6,0x473953)];INTERIOR=[(0x64CE5B,0x473AFF)]
ROUTES=[
 ("replace_display_thread_initialize","open_cfw_display_thread_initialize"),
 ("replace_display_queue_initialize","open_cfw_display_queue_initialize"),
 ("replace_display_thread_deinitialize","open_cfw_display_thread_deinitialize"),
 ("replace_display_resource_acquire","open_cfw_display_resource_acquire"),
 ("replace_display_resource_release","open_cfw_display_resource_release"),
 ("replace_display_timer_initialize","open_cfw_display_timer_initialize"),
 ("replace_display_timer_start","open_cfw_display_timer_start"),
 ("replace_display_timer_stop","open_cfw_display_timer_stop"),
 ("replace_display_timer_callback","open_cfw_display_timer_callback"),
 ("replace_display_queue_command8","open_cfw_display_queue_command8"),
 ("replace_display_manager_thread","open_cfw_display_manager_thread"),
 ("replace_display_clear_screen","open_cfw_display_clear_screen"),
 ("replace_display_initialize_async","open_cfw_display_initialize_async"),
 ("replace_display_power_up","open_cfw_display_power_up"),
 ("replace_display_power_down","open_cfw_display_power_down"),
 ("replace_display_brightness_control","open_cfw_display_brightness_control"),
 ("replace_display_send_reflash","open_cfw_display_send_reflash"),
 ("replace_display_initialize_force","open_cfw_display_initialize_force"),
 ("replace_display_deinitialize_force","open_cfw_display_deinitialize_force"),
]
SOURCES={
 "components/apollo_main/core_overlay/display_thread_init.c":"00f07bb6e27608257d27b4712112e06359c88ff1b3808124d5caf67497bafb15",
 "components/apollo_main/core_overlay/display_runtime.c":"a00a2b5cdf294275721acf567312b3a75bbce42ca3861b847d233772be15f046",
 "components/apollo_main/core_overlay/display_manager_thread.c":"3d198f983ffffe17a1ce9dcaa3c06042d068277d4c84846cdd885dec0f9adead",
 "components/apollo_main/core_overlay/display_queue_senders.c":"2d785865ba14c4b939c455e3d27772a7e935bc675b405357b80063b73d6d9a2f",
 "components/apollo_main/core_overlay/display_lifecycle.c":"17804ceaee55d54e204c0fd8c2ac889d1fbbc9340116d9084489ac94bbc56337",
}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());kernel=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text())
 if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or kernel["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c":raise c.AuditError("RTOS changed")
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
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2796 or sh(body)!="053b347c834d8d81fa732b56cb7d51caaa8c74257409d12da33a47f02d2ebf5b" or len(ins)!=1035 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="1ed4717bcb09d8e67421dba23db69b07f0440fa569d89f7ff960881655da9d9a" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=274 or sh(non)!="7cb8ecf6692ad871012b3758052169c6db3a4a75b713d6617817579ecbf551f4" or sh(c._slice(b,*PHYS))!="629e676c9b4bef5a15ccc3c26d640e8b3e3878f0064d03d4c94124785c085154":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="f225ff91ecc981b19811b75e3a7af2519ff233ab409af653954aa436d7835410" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="a46aae0429219892781600c9da3db366fcadeeaec7c5308bcc45b4b3922ef6e7":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,IAR,FIRST)
 if len(calls)!=184 or sum(y in starts for x,y in calls)!=6 or c._pair_digest(calls)!="5d13eb099513e25d71c4b2c2bef9ac79d5a28282d23af465dbf7d9ed17cfa5fa" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(125,20,11,22):raise c.AuditError("provider accounting changed")
 entries=[];strict=[];noncode_hits=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode_hits.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!="d4f43711b710d0122003dc76544ae7bc5a9c09f18fa2cfbbcb0852a708cc7af8" or strict or noncode_hits!=[(PSEUDO[0],PSEUDO[1])]:raise c.AuditError("BL ingress changed")
 decoder=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);i=next(decoder.disasm(c._slice(b,PSEUDO[2],PSEUDO[2]+4),PSEUDO[2]),None)
 if i is None or i.size!=4 or i.mnemonic!="udiv" or PSEUDO[0]!=PSEUDO[2]+2:raise c.AuditError("pseudo-BL proof changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 if [(a,v) for a,v in words if v in enc]!=STORED or [(a,v) for a,v in words if (v&1) and (v&~1) in inter]!=INTERIOR or (INTERIOR[0][1]&~1) not in ins:raise c.AuditError("stored entry closure changed")
 if cstring(b,0x6ECB68)!=r"D:\01_workspace\s200_ap510b_iar_git\platform\display_mgr\displaydrv_manager.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=25 or c._pair_digest(pairs)!="f3defc2f8126ca77f41a2f4c39e14e291e82f7fad1ce375e3d14ad328eaebca7":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 source_records={x["path"]:x for x in overlay["sources"] if x["path"] in SOURCES}
 if set(source_records)!=set(SOURCES):raise c.AuditError("display manager source inventory changed")
 for path,digest in SOURCES.items():
  if source_records[path].get("sha256")!=digest or sh((ROOT/path).read_bytes())!=digest:raise c.AuditError(f"display manager source changed: {path}")
 sites={x["name"]:x for x in overlay["patch_sites"]}
 routed=0
 for index,((name,target),(a,z)) in enumerate(zip(ROUTES,F)):
  site=sites.get(name);end=0x00473C44 if index==9 else z
  if site is None or site.get("runtime_address")!=a or site.get("target_function")!=target or site.get("branch")!="b_w" or site.get("expected_size")!=end-a or site.get("expected_sha256")!=sh(c._slice(b,a,end)):raise c.AuditError(f"display manager production route changed: {name}")
  if target not in overlay["functions"]:raise c.AuditError(f"display manager target missing: {target}")
  routed+=end-a
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"platform\display_mgr\displaydrv_manager.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":19,"ghidra_discovered_functions":12,"restored_functions":7,"path_anchored_functions":12,"body_bytes":2796,"physical_bytes":3070,"noncode_bytes":274,"reachable_instructions":1035,"direct_body_calls":184,"internal_direct_body_calls":6,"external_direct_body_calls":178,"indirect_body_calls":0,"direct_bl_entry_sites":18,"stored_function_entry_pointers":6,"stored_interior_callback_pointers":1,"raw_overlapping_pseudo_bl_sites":1,"strict_interior_ingress":0},"behavior":{"display_manager_lifecycle":True,"thread_and_timer_control":True,"uled_mspi_dispatch":True,"stored_completion_callbacks":True,"display_locking_and_state":True},"provider_boundary":{"easylogger_calls":125,"cmsis_freertos_calls":20,"iar_dlib_calls":11,"first_party_uled_display_calls":22,"direct_lvgl_calls":0,"direct_ambiqsuite_calls":0,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":True,"source_files":len(SOURCES),"guarded_redirects":len(ROUTES),"routed_stock_bytes":routed,"retained_compatibility_bytes":PHYS[1]-PHYS[0]-routed}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
