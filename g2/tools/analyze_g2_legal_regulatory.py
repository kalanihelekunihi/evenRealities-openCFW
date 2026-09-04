#!/usr/bin/env python3
"""Fail-closed audit of the G2 legal/regulatory UI object."""
import csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-legal-regulatory-function-map.tsv";CL=ROOT/"tools/manifests/g2-legal-regulatory-closure.tsv";PM=ROOT/"tools/manifests/g2-legal-regulatory-provider-map.tsv"
PINS={FM:"2da1776c1ab07820acb91fd1fe80964aa32b6e7ce20df7d39c4dffa8e8a33e5b",CL:"381f9033cc64b933d7b0b1eca13f0bd647c153f8447d1472da623a428a24d0b8",PM:"289340a802b57d2cde9faf7cd52ce8fc58b3069abc4d008b856af23951b3986c"};START,END,PHYS=0x5BF7B8,0x5BF8A2,(0x5BF7B8,0x5BF964)
SOURCE=ROOT/"components/apollo_main/core_overlay/legal_regulatory.c";HEADER=ROOT/"components/apollo_main/core_overlay/legal_regulatory.h";CONFIG=ROOT/"components/apollo_main/core_overlay/overlay.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
NAME="open_cfw_legal_regulatory_ui_event_handler";PATCH="replace_legal_regulatory_01"
SOURCE_PIN=(2067,"8916de06c518b2b54cb16bcba71328e43697580f6db8b20e26f2a923bdc8b744");HEADER_PIN=(354,"98dc8ac8fe337f0aac1edfa2dd8f62a7e2e11fc6e8711b520c6083b729ea8048")
PROVIDER_TARGETS=(0x005BF332,0x0058C238,0x0044EA04)
ROUTES={
 "apple-clang":{"path":ROOT/"components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin","report":ROOT/"components/apollo_main/core_overlay/build/build-report.json","component":"7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6","target":0x004B9738,"text":"ba4098df37d9a571693dd030f8d1e25b1e54a7c37977b4bafd33df56d485837e"},
 "linux-clang":{"path":ROOT/"build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin","report":ROOT/"build/canonical-observation-g2-final97/linux-b/build-report.json","component":"dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6","target":0x007BC310,"text":"274671c2f9cf2f6f5c3a756935b252d0fa0e2caa407ccdf5c704961c98513c6e"},
}
def sh(x):return hashlib.sha256(x).hexdigest()
def validate_production():
 for path,pin,label in ((SOURCE,SOURCE_PIN,"source"),(HEADER,HEADER_PIN,"header")):
  raw=path.read_bytes()
  if (len(raw),sh(raw))!=pin:raise c.AuditError(f"legal/regulatory production {label} changed")
 cfg=json.loads(CONFIG.read_text());leaves=[x for x in cfg.get("relocated_leaves",[]) if x.get("function")==NAME];patches=[x for x in cfg.get("patch_sites",[]) if x.get("name")==PATCH]
 if len(leaves)!=1 or len(patches)!=1:raise c.AuditError("legal/regulatory production inventory changed")
 leaf=leaves[0];linux=leaf.get("toolchain_profiles",{}).get("linux-clang",{});expected=(78,"0033f15b66f8d76e25d2c02e44bfc3bc5e290ea1fb4ba48209b796284382a60f")
 for record in (leaf,linux):
  relocations=record.get("relocations",[])
  if (record.get("expected",{}).get("size"),record.get("expected",{}).get("unrelocated_sha256"))!=expected or tuple(x.get("target_address") for x in relocations)!=PROVIDER_TARGETS:raise c.AuditError("legal/regulatory linked leaf pins changed")
 if leaf.get("profiles")!=["apple-clang","linux-clang"] or leaf.get("strict_relocation_contract") is not True or leaf.get("source",{}).get("sha256")!=SOURCE_PIN[1] or linux.get("reviewed_version_prefix")!="Homebrew clang version 22.1.8":raise c.AuditError("legal/regulatory profile contract changed")
 patch=patches[0]
 if patch.get("runtime_address")!=START or patch.get("expected_size")!=END-START or patch.get("target_function")!=NAME or patch.get("profiles")!=["apple-clang","linux-clang"]:raise c.AuditError("legal/regulatory patch contract changed")
 manifest=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"];offset=START-c.BASE;owners=[x for x in manifest["regions"] if x.get("file_offset",-1)<=offset<x.get("file_offset",-1)+x.get("size",0)]
 if len(owners)!=1 or owners[0].get("address_status") not in {"generated_source_entry_replacement","generated_source_data_replacement"}:raise c.AuditError("legal/regulatory manifest ownership changed")
 for profile,route in ROUTES.items():
  component=route["path"].read_bytes()
  if len(component)!=3956672 or sh(component)!=route["component"]:raise c.AuditError(f"{profile} legal/regulatory component changed")
  replacement=c._slice(component,START,END)
  if apollo_overlay.decode_thumb_branch(START,replacement[:4],link=False)!=route["target"] or replacement[4:]!=b"\x00\xbf"*((len(replacement)-4)//2):raise c.AuditError(f"{profile} legal/regulatory redirect changed")
  if sh(c._slice(component,route["target"],route["target"]+78))!=route["text"]:raise c.AuditError(f"{profile} legal/regulatory routed text changed")
  report=json.loads(route["report"].read_text());rows=[x.get("extraction",{}) for x in report.get("relocated_leaves",[]) if x.get("extraction",{}).get("function")==NAME]
  if len(rows)!=1 or rows[0].get("size")!=78 or rows[0].get("unrelocated_sha256")!=expected[1] or rows[0].get("relocation_count")!=3:raise c.AuditError(f"{profile} legal/regulatory build receipt changed")
 validate_apollo_main_artifacts(ROOT,c.AuditError,"production legal/regulatory UI")
 return {"candidate":str(SOURCE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT)),"production_routed":True,"source_inventory_available":True,"source_functions":1,"compiled_text_bytes":{"apple-clang":78,"linux-clang":78},"stock_body_bytes_displaced":234,"ownership_bytes":234,"retained_stock_noncode_bytes":194,"strict_relocations":3,"profiles_verified":["apple-clang","linux-clang"],"software_functional_gap":False,"hardware_validation":"blocked by unavailable physical evidence","hardware_evidence_required":["authorized G2 display trace proving legal/regulatory page creation, animated entry/exit, and scroll behavior against the device content table"],"hardware_operations":[]}
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=1:raise c.AuditError("function inventory changed")
 body=c._slice(b,START,END)
 if sh(body)!="99c67be892d730a8c6872d42af9a05f4d9906236efffe5365f1f5f76607933fb":raise c.AuditError("body changed")
 ins,calls,ind=d._recover_function(b,START,END);calls.sort()
 if len(ins)!=98 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="4c44989db5047b14b4a0518bf908b32b1068d06896d664e0cdffc4a8baa75722" or len(calls)!=15 or c._pair_digest(calls)!="d28b858f6821baf9fb7b2a3d6ae39d0b5c3f4a86549bd4ae968d4041c9283f1e" or ind:raise c.AuditError("code topology changed")
 if sh(c._slice(b,*PHYS))!="eec57b8478edf3d026cb90588c9ffcb5039bf78408d2e373cdffe6cdc1cf1151" or sh(c._slice(b,END,PHYS[1]))!="6dc058b8c38d7def8a5175fe48922df8b5ce6459e27c675fa1513d6802566422":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x5BF7A0,START))!="b70acd1c958c7ffb6d7078a136c8c87bb11ba58e9b9fcc8b8556ddc9230a5958" or sh(c._slice(b,PHYS[1],0x5BF972))!="41a7f17ded392fc42956b4da6c5adf28fbc75722b8181eddf5c9aeecb9837881":raise c.AuditError("boundary changed")
 stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0]
  if v in {START|1,0x5BF880|1}:stored.append((c.BASE+off,v&~1))
 if stored!=[(0x4B3C36,0x5BF880),(0x4B458E,0x5BF880),(0x6A4558,START)]:raise c.AuditError("stored/shared entries changed")
 if t._thumb_bl_target(b,0x5BB7FC)!=0x5BF88C:raise c.AuditError("shared direct tail changed")
 for a,s in {0x6ED838:r"D:\01_workspace\s200_ap510b_iar_git\app\gui\LegalRegulatory\legal_regulatory.c",0x760450:"LegalRegulatory display startup",0x760470:"LegalRegulatory display exit",0x754DC4:"legal_regulatory_ui_event_handler"}.items():
  if c._c_string(b,a)!=s:raise c.AuditError("string changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure plus dual-profile production-route verification","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":1,"body_bytes":234,"physical_bytes":428,"outer_pool_bytes":194,"direct_body_calls":15,"stored_primary_entry_pointers":1,"shared_tail_direct_entries":1,"shared_tail_stored_entries":2,"indirect_body_calls":0},"provider_boundary":{"easylogger_calls":10,"lvgl_calls":1,"iar_dlib_calls":2,"first_party_calls":2,"new_version_discriminator":False},"production":validate_production()}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
