#!/usr/bin/env python3
"""Fail-closed object/provider audit for ui_onboarding_stock_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-onboarding-stock-page-function-map.tsv";CL=ROOT/"tools/manifests/g2-onboarding-stock-page-closure.tsv";PM=ROOT/"tools/manifests/g2-onboarding-stock-page-provider-map.tsv"
PINS={FM:"f21a8ffa1538021ad689b2b88eac2bfcfb7d33feb2733bf08f7a0f077a0daaff",CL:"d53ed2fed6185d3a3cebe276423624bc7964ca01b12627e0f65891ebd0d0a7fb",PM:"4a67245db01102d4ea4ee161ea8d0082a2be9d7a6699d076a19552748c6331e5"}
PHYS=(0x50CA24,0x50E8DC)
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x44131C,0x44140E,0x44143E,0x44145A,0x44D7B8,0x44D878,0x44DCE2,0x44DDEA,0x44E368,0x498668,0x498680,0x499416,0x49942E,0x499678}
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4497B6,0x44981C};IAR={0x439BE4,0x43C0E4}
FIRST={0x45FFFE,0x460084,0x4A979C,0x4A9DE8,0x4A9EDC,0x509C1C,0x509C96,0x509CA2}
PATH_CELLS={0x50D554:[0x50CA76,0x50CAD4,0x50CB56,0x50D382],0x50DC58:[0x50D5A0,0x50D5F0,0x50D698,0x50D704,0x50D76A,0x50D834,0x50D8B4,0x50D91E,0x50D97A,0x50DA6C,0x50DB52,0x50DBC8],0x50E720:[0x50DCE6,0x50DD46,0x50DDAA,0x50E4AA],0x50E974:[0x50E832,0x50E8B2]}
INLINE=[(0x50CC8A,0x50CC90),(0x50DDDC,0x50DDE0)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());kernel=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or cmsis["upstreams"]["cmsis_5"]["selected_commit"]!="2b7495b8535bdcb306dac29b9ded4cfb679d7e5c" or kernel["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c":raise c.AuditError("RTOS/logger provenance changed")
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
 if len(F)!=17 or sum(r['source_path_anchor']=='yes' for r in rows)!=10:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if uncovered!=INLINE or b''.join(c._slice(b,a,z) for a,z in INLINE).hex()!="00bf00000000bc420020":raise c.AuditError("inline literals changed")
 if len(body)!=7500 or sh(body)!="83aef97c1aa3729449435f2392335bc6e924b259edadcf3d51ad1af4538ad844" or len(ins)!=2818 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="c0e9ee45ed98a5c979c401d0f3083cf5f0828d08e536bb69aeea01cd8f5a8d4f" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=364 or sh(non)!="8b17ba5cd877b155887cefda551350479138bfac21d55726aef5bfd4475055ff" or sh(c._slice(b,*PHYS))!="3b101a0ddd84ec458063fa6815a4b5b1c6684ecbfe5efedcfb104cbdc69b0695":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,0x50CA14,PHYS[0]))!="d5ffb439f7308cbdcfac7c9daee8d279f2689a7727fbecfa8b738aa1816c7018" or sh(c._slice(b,PHYS[1],0x50E8EC))!="2abc6fece563956ec746655d39bdcb3d64b4530778108192a2fa9a06f64eebdb":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(LVGL,EASY,CMSIS,IAR,FIRST)
 if len(calls)!=629 or sum(y in starts for x,y in calls)!=32 or c._pair_digest(calls)!="ce0f9a89923b3fc9af9fe8b0825bf0a6c8858a4d8b7c70625d3172629a647dbc" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(447,110,2,5,33):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=38 or c._pair_digest(entries)!="577a701149980ab044e8363116f6747041269eda8b90efa2d9be28ab709ff2ab" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored:raise c.AuditError("stored callbacks changed")
 if cstring(b,0x6EAB58)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_stock_page.c":raise c.AuditError("path changed")
 for cell,refs in PATH_CELLS.items():
  if t.literal_references(b,cell)!=refs:raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("ui_onboarding_stock_page" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\onboarding\ui_onboarding_stock_page.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":17,"ghidra_discovered_functions":17,"restored_functions":0,"path_anchored_functions":10,"body_bytes":7500,"physical_bytes":7864,"noncode_bytes":364,"reachable_instructions":2818,"direct_body_calls":629,"internal_direct_body_calls":32,"external_direct_body_calls":597,"indirect_body_calls":0,"direct_bl_entry_sites":38,"stored_entry_pointers":0,"strict_interior_ingress":0},"behavior":{"stock_page_construction_and_layout":True,"three_item_paging_and_visibility":True,"stock_data_copy_and_render":True,"main_page_and_controller_integration":True,"mutex_serialized_page_state":True},"provider_boundary":{"lvgl_calls":447,"easylogger_calls":110,"cmsis_freertos_calls":2,"iar_dlib_calls":5,"first_party_calls":33,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
