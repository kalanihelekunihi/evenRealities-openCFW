#!/usr/bin/env python3
"""Fail-closed object/provider audit for health_data_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-health-data-manager-function-map.tsv";PM=ROOT/"tools/manifests/g2-health-data-manager-provider-map.tsv";CL=ROOT/"tools/manifests/g2-health-data-manager-closure.tsv"
PROD=ROOT/"components/apollo_main/core_overlay/health_data_manager.c";OVERLAY=ROOT/"components/apollo_main/core_overlay/overlay.json";REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
PINS={FM:"6e850bd713482629f98fa8aff0f7c263eb22f11b0e884d1a1d1a3c7278865284",PM:"ec85e7940ba073dc806224fed24792b021edee41f942c2d66e5f3a1bdf7481f9",CL:"b4a67632e1c7f2e55274304a9b2a38f32e0197a874506095496e79a6ae086e55"}
PHYS=(0x5597F0,0x55A350);PATH_CELLS=(0x559FAC,0x55A30C);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};HEALTH={0x4FFC32,0x4FFC90}
PROD_PIN=(15863,"42df69101ab924e6b9e6f2710d618ab9a5e57c8154d3b135eeffdfadf195c5fd")
LEAVES=(
 ("open_cfw_health_data_type_index","OPEN_CFW_HEALTH_DM_INDEX_ONLY",18,"beec3042f4f13f78d76daa14c1e5e4b42bbcb5274a85e636670ae6870b89599d",242400),
 ("open_cfw_health_data_slot_for_type","OPEN_CFW_HEALTH_DM_SLOT_ONLY",32,"a947fa832da884244a39b56b66e13e3fb14bd7cbe9f86d6ddf8b3e24a010bf13",242420),
 ("open_cfw_health_data_type_name","OPEN_CFW_HEALTH_DM_NAME_ONLY",154,"73058404209be1f6138313ba6ef19e3e774a80ed488cddd823cd1eed72dd4570",242452),
 ("open_cfw_health_data_manager_init","OPEN_CFW_HEALTH_DM_INIT_ONLY",210,"8d34220b5e8e12be5e629f356ab89fe440344dd2334a77886c90a812c440b115",242608),
 ("open_cfw_health_data_convert_from_pb","OPEN_CFW_HEALTH_DM_CONVERT_ONLY",100,"8aef36b4af097948fb0f6db1425ddad9fc50867a3fcf65b0b8c9c2d9ee63e819",242820),
 ("open_cfw_health_data_save_single","OPEN_CFW_HEALTH_DM_SAVE_SINGLE_ONLY",54,"d0dbe75c743a36abbd9d214bb0c35c4348a28cc273083eb8091138c67192d12e",242920),
 ("open_cfw_health_data_save_multiple","OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_ONLY",72,"bc0b9420a2d3f6c4ffdd493e4b6b541a95c6d14b57b89b16dd04c24a7c047534",242976),
 ("open_cfw_health_data_convert_highlight_from_pb","OPEN_CFW_HEALTH_DM_CONVERT_HIGHLIGHT_ONLY",134,"83d81bc843e822d684638e83cf15f6f4e498a6fb526912fa60094e68735a4116",243048),
 ("open_cfw_health_data_save_single_highlight","OPEN_CFW_HEALTH_DM_SAVE_SINGLE_HIGHLIGHT_ONLY",96,"7cd5ad2e9c9ffa4c3b803369ae07ff8a974d919294368fcd09b9f337db023fca",243184),
 ("open_cfw_health_data_save_multiple_highlights","OPEN_CFW_HEALTH_DM_SAVE_MULTIPLE_HIGHLIGHTS_ONLY",142,"dcd2043e2beffcf2f68d7d3a275b6397363cc567ebeca68b0e7e4a4229f43624",243280),
)
STOCK_TARGETS={
 0x5597F0:"open_cfw_health_data_type_index",0x559836:"open_cfw_health_data_slot_for_type",0x559854:"open_cfw_health_data_type_name",0x5598AE:"open_cfw_health_data_manager_init",0x5598CC:"open_cfw_health_data_save_single",0x559AD2:"open_cfw_health_data_save_multiple",0x559D82:"open_cfw_health_data_convert_from_pb",0x559DFC:"open_cfw_health_data_save_single_highlight",0x559FB8:"open_cfw_health_data_save_multiple_highlights",0x55A230:"open_cfw_health_data_convert_highlight_from_pb",
}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
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
 if len(F)!=10 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2644 or sh(body)!="050ec6e745b00b6d6cfd37b83e2283415053a3f7e486e7bdff3a59ddccf541f4" or len(ins)!=976 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="41b051dcd8a6aa9d7322e196e189090968bd1e5dd6f49ffcd21657fa49fb9df4" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=268 or sh(non)!="243baf3a6d20197747a4cff17cb20485fa07895c4a267566fb134e8a493d37ca" or sh(c._slice(b,*PHYS))!="44352a771275d97318b726f9525fbff941a6f11bdc761736e0317a407ca3b2ae":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="260a519ad8da8666c618201c1a50a5ade32d8153dd491349f4e261e3eec761da" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="5cbaf0bff77f2af89d0f87730938566cc5456c30ce660918a34d10379e48581d":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,HEALTH)
 if len(calls)!=149 or sum(y in starts for x,y in calls)!=13 or c._pair_digest(calls)!="76897902ad5c523275572a03d364a4bdcf66ef46351845d83242087cacef47fd" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(120,6,10):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!="361456eea75ebc902cdaee6008b33e3956f575fc91d9641d218b536f179e4f73" or strict:raise c.AuditError("raw ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or interior:raise c.AuditError("stored entry closure changed")
 if cstring(b,0x6F3E00)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\health\health_data_manager.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=24 or c._pair_digest(pairs)!="f01b62d30614e6314d703baf8b8bda5204c4d5d1b1273ffd6a7602d0303e01e4":raise c.AuditError("path references changed")
 prod=PROD.read_bytes()
 if (len(prod),sh(prod))!=PROD_PIN:raise c.AuditError("production health data manager changed")
 overlay=json.loads(OVERLAY.read_text());leaf_names={x[0] for x in LEAVES}
 selected={x.get("function"):x for x in overlay.get("relocated_leaves",[]) if x.get("function") in leaf_names}
 if set(selected)!=leaf_names or not leaf_names.issubset(set(overlay.get("functions",[]))):raise c.AuditError("production health leaf inventory changed")
 relocation_count=0
 for name,selector,size,digest,offset in LEAVES:
  leaf=selected[name];src=leaf.get("source",{});tool=leaf.get("toolchain",{});pin=leaf.get("expected",{})
  if src.get("path")!="components/apollo_main/core_overlay/health_data_manager.c" or (src.get("size"),src.get("sha256"))!=PROD_PIN or leaf.get("profiles")!=["apple-clang"] or not leaf.get("strict_relocation_contract"):raise c.AuditError(f"production contract changed: {name}")
  if f"-D{selector}=1" not in tool.get("flags",[]) or (pin.get("size"),pin.get("sha256"),pin.get("alignment"),pin.get("offset"))!=(size,digest,4,offset):raise c.AuditError(f"production pin changed: {name}")
  relocation_count+=len(leaf.get("relocations",[]))
 if relocation_count!=15:raise c.AuditError("production relocation closure changed")
 sites={x.get("runtime_address"):x for x in overlay.get("patch_sites",[]) if x.get("runtime_address") in STOCK_TARGETS}
 if set(sites)!=set(STOCK_TARGETS):raise c.AuditError("production entry routing changed")
 for row,(a,z) in zip(rows,F):
  site=sites[a]
  if site.get("expected_size")!=z-a or site.get("expected_sha256")!=row["stock_sha256"] or site.get("target_function")!=STOCK_TARGETS[a] or site.get("branch")!="b_w" or site.get("profiles")!=["apple-clang"]:raise c.AuditError("production stock replacement changed")
 report=json.loads(REPORT.read_text())
 if (report["overlay"]["size"],report["overlay"]["sha256"],report["component"]["size"],report["component"]["sha256"])!=(332148,"588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d",3855544,"df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc"):raise c.AuditError("production build pins changed")
 built={x.get("extraction",{}).get("function"):x for x in report.get("relocated_leaves",[]) if x.get("extraction",{}).get("function") in leaf_names}
 if set(built)!=leaf_names or sum(x[2] for x in LEAVES)!=1012 or sum(x["placement"].get("padding_before",0) for x in built.values())!=10:raise c.AuditError("production compiled closure changed")
 manifest=json.loads(MANIFEST.read_text());main=manifest["component_overrides"]["apollo_main"];regions=main["regions"]
 generated=[x for x in regions if x.get("address_status")=="generated_source_entry_replacement" and x.get("target_address") in STOCK_TARGETS]
 appended=[x for x in regions if x.get("address_status")=="source_compiled" and 8189444<=x.get("target_address",0)<8190466]
 if len(generated)!=10 or sum(x["size"] for x in generated)!=2644 or len(appended)!=10 or sum(x["size"] for x in appended)!=1012:raise c.AuditError("production manifest closure changed")
 if (main["provider"]["size"],main["provider"]["sha256"],manifest["package"]["expected_size"],manifest["package"]["expected_sha256"])!=(3855544,"df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",4634038,"3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731"):raise c.AuditError("production package pins changed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\health\health_data_manager.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":10,"ghidra_discovered_functions":9,"restored_functions":1,"path_anchored_functions":5,"body_bytes":2644,"physical_bytes":2912,"noncode_bytes":268,"reachable_instructions":976,"direct_body_calls":149,"internal_direct_body_calls":13,"external_direct_body_calls":136,"indirect_body_calls":0,"direct_bl_entry_sites":18,"stored_function_entry_pointers":0,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":120,"iar_runtime_calls":6,"closed_health_lock_calls":10,"direct_cmsis_freertos_calls":0,"historical_health_manager_commit":None,"new_version_discriminator":False},"production":{"production_routed":True,"source_functions":10,"compiled_text_bytes":1012,"alignment_bytes":10,"stock_replaced_bytes":2644,"strict_relocations":15,"software_functional_gap":False,"hardware_validation":"blocked","hardware_blocker":"No authorized physical G2/EM9305 hardware evidence is available in this workspace."}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
