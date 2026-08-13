#!/usr/bin/env python3
"""Fail-closed object/provider audit for ui_onboarding_news_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-onboarding-news-page-function-map.tsv";CL=ROOT/"tools/manifests/g2-onboarding-news-page-closure.tsv";PM=ROOT/"tools/manifests/g2-onboarding-news-page-provider-map.tsv"
PINS={FM:"2c4ba2698f7cdf6664b7b3686d55991c5b83e2284b878f731af253136fd766ab",CL:"d763caa06da0bdcf73d12412ca455d4309a3040fe561d2f332145fc411014713",PM:"597175c92ddb66d560072cf7773052e7f8a796eafe467c503d799bf35e4b2ab8"}
PHYS=(0x50A094,0x50CA24)
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E0E0,0x43E2EA,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6B8,0x43F6D6,0x43FCE0,0x43FDDA,0x44104C,0x441164,0x44120E,0x44121C,0x44122A,0x441238,0x441254,0x44127E,0x44129E,0x4412EC,0x44131C,0x44133A,0x441378,0x441386,0x441394,0x4413A2,0x4413B0,0x44140E,0x44142E,0x44143E,0x44145A,0x44146A,0x44D7B8,0x44D878,0x44DCA2,0x44DCE2,0x44DDEA,0x44E368,0x44E3CA,0x44E498,0x44E4AA,0x44E4BC,0x44EA04,0x4503D6,0x450408,0x450500,0x4506CE,0x498668,0x498680,0x499416,0x49942E,0x499678}
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4497B6,0x44981C};IAR={0x439BE4,0x439C04,0x43C0E4,0x44B728};TIME={0x44A100,0x44A19A};EABI={0x47CC60}
FIRST={0x45FFFE,0x460084,0x464BB2,0x48BA78,0x48BA92,0x4A93B0,0x4A96DC,0x4A979C,0x4A9DE8,0x4A9EDC,0x509C1C,0x509C96,0x509DFA,0x509E14,0x509FDC,0x50A010}
PATH_CELLS={0x50AC24:[0x50A0FA,0x50A4B0,0x50A696,0x50AB20,0x50AB68],0x50B5D8:[0x50ACA2,0x50AFCA,0x50B07C,0x50B0E6,0x50B4A0],0x50B73C:[0x50B626,0x50B67E],0x50C2F8:[0x50B772,0x50B7C6,0x50B874,0x50B8DE,0x50B988,0x50BA1A,0x50BB16,0x50BB8A,0x50BBF0,0x50BE88,0x50BEE0,0x50C04A,0x50C188,0x50C1F0,0x50C2C4],0x50C9C4:[0x50C38A,0x50C424,0x50C550,0x50C5B8,0x50C60C,0x50C678,0x50C718]}
PSEUDO=[(0x48A484,0x50A5A2,0x48A482),(0x48A4A4,0x50A5C2,0x48A4A2)]
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
 if "0x0047CC60" not in (ROOT/"components/apollo_main/core_overlay/EVIDENCE.md").read_text() or not (ROOT/"components/apollo_main/core_overlay/aeabi_divmod.c").is_file():raise c.AuditError("ARM EABI source ownership changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=35 or sum(r['source_path_anchor']=='yes' for r in rows)!=19:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if uncovered or len(body)!=9346 or sh(body)!="c7d787866bf0de56a149c60ea18d5e717866420d6b6e3d9ddfd27c358b74ccd4" or len(ins)!=3494 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="96e035ac5eb944688c5555703d781dceb8603623777367deb59cf7871e1c203f" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=1294 or sh(non)!="59f5c65b8e6bc63d003011c460deece8a3f72dcf6b300aa2f6088ffa35cb9532" or sh(c._slice(b,*PHYS))!="e037ab6c2c7f120b620c816743dfec986a79a5e204e781bfca2d2b23c597670b":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,0x50A084,PHYS[0]))!="35a2a03900473c08925b2aae072fd8dc8f72f9cf4ad26d1d818dd12c0705bf1f" or sh(c._slice(b,PHYS[1],0x50CA34))!="99fd64635c441e7613735960b036bdcf4740e0fed41eb221a7cb485069b2fb24":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(LVGL,EASY,CMSIS,IAR,EABI,TIME,FIRST)
 if len(calls)!=544 or sum(y in starts for x,y in calls)!=74 or c._pair_digest(calls)!="f84b0dd5aa88f2f522299ea7cc42407e2615933e84989f0d9b9c52c0ecf0e16e" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(232,160,16,15,1,2,44):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=85 or c._pair_digest(entries)!="cb4e252c21ff150809283269148f6a18918cf5ee11e66ee67529cfb228c5463f" or strict!=[(a,y) for a,y,_ in PSEUDO]:raise c.AuditError("raw ingress changed")
 outer,_,_=q._recover_function(b,0x48A0BE,0x48A74A)
 for site,target,cover in PSEUDO:
  i=outer.get(cover)
  if i is None or i.size!=4 or i.mnemonic!="uxtab" or site!=cover+2:raise c.AuditError("pseudo-BL overlap proof changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x50C9A4,0x50BE4D)]:raise c.AuditError("stored callback changed")
 if cstring(b,0x6EAB04)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_news_page.c":raise c.AuditError("path changed")
 for cell,refs in PATH_CELLS.items():
  if t.literal_references(b,cell)!=refs:raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("ui_onboarding_news_page" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\onboarding\ui_onboarding_news_page.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":35,"ghidra_discovered_functions":35,"restored_functions":0,"path_anchored_functions":19,"body_bytes":9346,"physical_bytes":10640,"noncode_bytes":1294,"reachable_instructions":3494,"direct_body_calls":544,"internal_direct_body_calls":74,"external_direct_body_calls":470,"indirect_body_calls":0,"direct_bl_entry_sites":85,"stored_entry_pointers":1,"raw_overlapping_pseudo_bl_sites":2,"strict_interior_ingress":0},"behavior":{"news_page_construction_and_layout":True,"news_record_copy_and_render":True,"scroll_and_page_state":True,"time_formatting":True,"main_page_and_controller_integration":True,"mutex_serialized_page_state":True},"provider_boundary":{"lvgl_calls":232,"easylogger_calls":160,"cmsis_freertos_calls":16,"iar_dlib_calls":15,"source_owned_aeabi_calls":1,"closed_time_service_calls":2,"first_party_calls":44,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
