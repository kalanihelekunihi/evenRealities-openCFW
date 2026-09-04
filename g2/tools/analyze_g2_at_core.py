#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for eAT at_core.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-at-core-function-map.tsv";CL=ROOT/"tools/manifests/g2-at-core-closure.tsv";PM=ROOT/"tools/manifests/g2-at-core-provider-map.tsv"
PINS={FM:"853b81d8aea60d430d541befc26d9221b5c4c1024ead25919bcab3b8e7ad9809",CL:"089850a2461609ff7688d7728bfcbb09ebf3187300640dfb5ef8e9977b0fabdc",PM:"ade616b5c70094a51481c5230f4f0152099b5960f1881f1aabfcf0d2116a4f9b"};F=((0x5412E0,0x541302),(0x541302,0x54136C),(0x54136C,0x541430),(0x541430,0x5414BA),(0x5414BA,0x54157A));PHYS=(0x5412E0,0x5415B4);POOL=(0x54157A,0x5415B4)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4,0x44A43C,0x44B728,0x44B76C,0x4751C8};FIRST={0x57DDFC,0x57DE0A,0x57DEB0};IND=[0x54149A,0x5414B0,0x54147E,0x5414F6]
SOURCE=ROOT/"components/apollo_main/core_overlay/at_core.c";HEADER=ROOT/"components/apollo_main/core_overlay/at_core.h";CONFIG=ROOT/"components/apollo_main/core_overlay/overlay.json";REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
NAMES=("open_cfw_at_core_register_callback","open_cfw_at_core_init","open_cfw_at_core_handler","open_cfw_at_core_output","open_cfw_at_core_dispatch_command")
PATCHES=tuple(f"replace_at_core_{i:02d}" for i in range(1,6))
SOURCE_PIN=(8618,"f5a51a567b7793c6527c374da46232c23accb1b43c621edb6b7e43ce593f76d1");HEADER_PIN=(1238,"bce386303a711af303fe2124cdc07d03695d498dea1434e23596cfe18455c282")
ROUTES={
 "apple-clang":{"path":ROOT/"components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin","component":"90899422791207c0f91d9fd3c54dcba2bba8ebc6797de47ff5014b60c070d9df","targets":(0x4BBC58,0x4BA568,0x4580C4,0x490088,0x455DC4),"sizes":(34,42,582,116,328),"text":("0a9a739800df12a9c62a283d2f635b7fa6afa056daf03242f95fbd3c6a52ea82","96f54c2937b6a5d73c477a17237fe90d1d782d408a04cee1635ef3b607f17e32","cd23b82129a6b58b013e164985f127fa970f960827f4cf48bc74a4e7fb295acc","4b8eb78b20c7f9d6a6451b72600d9d8bddcaf1ee554221abee3a129a053f89e1","a9ccd77d8ab248517fb49e6d19eba7909daa324975133db2919713b2e874664c")},
 "linux-clang":{"path":ROOT/"build/canonical-provider/linux-clang/apollo_main/ota_s200_firmware_ota.bin","component":"918c5888ac8b417efa21fc406de63ccffd8d9a5a24c5b80d18ec51d37e9a1a50","targets":(0x7BB884,0x7BB8A8,0x7BB8D4,0x7BBB34,0x7BBBA8),"sizes":(34,42,606,116,366),"text":("0a9a739800df12a9c62a283d2f635b7fa6afa056daf03242f95fbd3c6a52ea82","00c983d58ce8680921524834460e07a19f4212ff841796a09d405f1d9f47b477","5512822ff65f172eb6c2125947cd488bc8e5f40353939dd43ac6d3bec206902c","cfb4d518c427e7e2b3f982c59dce577dbbe78b7e1126dfaccfe07ffb0260147c","e0636e04757ce38abe7707e566693c689cdc68436ed4a388813ba4b4cd5fa510")},
}
ROUTES["apple-clang"].update(
    component="7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
    targets=(0x4C4B2C, 0x4C499C, 0x4580C4, 0x46CEDC, 0x455DC4),
    text=("0a9a739800df12a9c62a283d2f635b7fa6afa056daf03242f95fbd3c6a52ea82","234e102d8f75722b276367dd18f7186b6074fd2ea866ffff78724fd204dca68c","cd23b82129a6b58b013e164985f127fa970f960827f4cf48bc74a4e7fb295acc","c5f345ec2d7be6be3522b02815b3a36037146dabead9d3e473fa426ab883e2fc","a9ccd77d8ab248517fb49e6d19eba7909daa324975133db2919713b2e874664c"),
)
ROUTES["linux-clang"].update(
    path=ROOT/"build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin",
    component="dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
)
def sh(x):return hashlib.sha256(x).hexdigest()
def _slice_component(blob,start,size):
 off=start-c.BASE;return blob[off:off+size]
def _validate_production():
 for path,pin,label in ((SOURCE,SOURCE_PIN,"source"),(HEADER,HEADER_PIN,"header")):
  raw=path.read_bytes()
  if (len(raw),sh(raw))!=pin:raise c.AuditError(f"at_core production {label} changed")
 cfg=json.loads(CONFIG.read_text());leaves={x.get("function"):x for x in cfg["relocated_leaves"] if x.get("function") in NAMES}
 if set(leaves)!=set(NAMES):raise c.AuditError("at_core production leaf inventory changed")
 expected_relocs=(0,1,3,1,1);expected_targets=((),(0x57DDFC,),(0x57DEB0,0x57DEB0,0x494170),(0x44B76C,),(0x57DE0A,))
 for i,name in enumerate(NAMES):
  leaf=leaves[name]
  if leaf.get("profiles")!=["apple-clang","linux-clang"] or leaf.get("strict_relocation_contract") is not True or leaf.get("source",{}).get("sha256")!=SOURCE_PIN[1] or len(leaf.get("relocations",[]))!=expected_relocs[i] or tuple(x.get("target_address") for x in leaf.get("relocations",[]))!=expected_targets[i]:raise c.AuditError(f"at_core production pins changed: {name}")
  linux=leaf.get("toolchain_profiles",{}).get("linux-clang",{})
  if linux.get("reviewed_version_prefix")!="Homebrew clang version 22.1.8" or len(linux.get("relocations",[]))!=expected_relocs[i]:raise c.AuditError(f"at_core Linux pins changed: {name}")
 patches={x.get("name"):x for x in cfg["patch_sites"] if x.get("name") in PATCHES}
 if set(patches)!=set(PATCHES):raise c.AuditError("at_core production patch inventory changed")
 for name,function,bounds in zip(PATCHES,NAMES,F):
  patch=patches[name]
  if patch.get("runtime_address")!=bounds[0] or patch.get("expected_size")!=bounds[1]-bounds[0] or patch.get("target_function")!=function or patch.get("profiles")!=["apple-clang","linux-clang"]:raise c.AuditError(f"at_core production patch changed: {name}")
 report=json.loads(REPORT.read_text());built={x.get("extraction",{}).get("function"):x for x in report["relocated_leaves"] if x.get("extraction",{}).get("function") in NAMES}
 if set(built)!=set(NAMES):raise c.AuditError("at_core built leaf inventory changed")
 manifest=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"]
 for start,_end in F:
  off=start-c.BASE;owners=[x for x in manifest["regions"] if x.get("file_offset",-1)<=off<x.get("file_offset",-1)+x.get("size",0)]
  if len(owners)!=1 or owners[0].get("address_status") not in {"generated_source_entry_replacement","generated_source_data_replacement"}:raise c.AuditError("at_core manifest entry ownership changed")
 pool_off=POOL[0]-c.BASE;pool_owner=[x for x in manifest["regions"] if x.get("file_offset",-1)<=pool_off<x.get("file_offset",-1)+x.get("size",0)]
 if len(pool_owner)!=1 or pool_owner[0].get("address_status")!="official_blob":raise c.AuditError("at_core diagnostic pool ownership changed")
 for profile,route in ROUTES.items():
  component=route["path"].read_bytes()
  if len(component)!=3956672 or sh(component)!=route["component"]:raise c.AuditError(f"{profile} at_core component changed")
  for bounds,target,size,digest in zip(F,route["targets"],route["sizes"],route["text"]):
   replacement=_slice_component(component,bounds[0],bounds[1]-bounds[0])
   if apollo_overlay.decode_thumb_branch(bounds[0],replacement[:4],link=False)!=target or replacement[4:]!=b"\x00\xbf"*((len(replacement)-4)//2):raise c.AuditError(f"{profile} at_core redirect changed")
   if sh(_slice_component(component,target,size))!=digest:raise c.AuditError(f"{profile} at_core compiled text changed")
 validate_apollo_main_artifacts(ROOT,c.AuditError,"eAT core")
 return {"candidate":str(SOURCE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT)),"production_routed":True,"source_inventory_available":True,"source_functions":5,"compiled_text_bytes":{"apple-clang":1102,"linux-clang":1164},"alignment_bytes":{"apple-clang":6,"linux-clang":6},"strict_relocations":6,"stock_body_bytes_displaced":666,"retained_diagnostic_pool_bytes":58,"profiles_verified":["apple-clang","linux-clang"],"software_functional_gap":False,"hardware_validation":"blocked by unavailable physical evidence","hardware_evidence_required":["authorized G2 command-table dispatch trace","authorized G2 callback/output transport trace"],"hardware_operations":[]}
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=5:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=2 or len(body)!=666 or sh(body)!="1a4a9470df59605ee0655a824f38edd00bf481589640c432717967c40c3b4eb5" or code!=body or len(ins)!=281 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="36487bc5e3e7ac0f50fc784fb357310b9affbe9daf33e080e44733c45820bd91":raise c.AuditError("instruction closure changed")
 if ind!=IND or d._address_digest(ind)!="8a05955e46f6fafd5f098d17916b2d3738970a4764256005e6b50445520843e4":raise c.AuditError("indirect call topology changed")
 if sh(c._slice(b,*PHYS))!="ffe5d0bebdc722a192977f973922b2915aa66e0e0c1083ef673acab29a638e0a" or sh(c._slice(b,*POOL))!="d672f0e669a363d991186dfaf619e555ea115bc373776000166151bccfeeeef3":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x5412D8,PHYS[0]))!="5330b09d070eadb9e62b3d1fee341cf881d16d5bc64bd2ff0f75021d808a3787" or sh(c._slice(b,PHYS[1],0x5415C2))!="f95db635787d3076786e44cf1c634d50ae9761506e0eadc2a5a71967c40e67ae":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts)
 if len(calls)!=21 or sum(y in starts for _,y in calls)!=1 or c._pair_digest(calls)!="89dc77834666ef37361d8fa61d982fc93bf6ead8bd47251be48b8d4fd62f9c39" or set(ext)!=EASY|IAR|FIRST:raise c.AuditError("call topology changed")
 if (sum(ext[x] for x in EASY),sum(ext[x] for x in IAR),sum(ext[x] for x in FIRST))!=(10,6,4):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=85 or c._pair_digest(entries)!="2890ada6cbd2be926b11acb7157afccae03f6001498290b4a3119f2711fd5819" or strict:raise c.AuditError("BL entry topology changed")
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];target=v&~1
  if v&1 and (target in starts or target in interiors):raise c.AuditError("unexpected stored entry")
 if t.literal_references(b,0x541594)!=[0x541342,0x5413E0]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure plus dual-profile production-route verification; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[],"public_source_fingerprint_match":False},"surface":{"linked_functions":5,"ghidra_discovered_functions":4,"additional_recovered_functions":1,"path_anchored_functions":2,"body_bytes":666,"physical_bytes":724,"outer_pool_bytes":58,"direct_body_calls":21,"internal_direct_body_calls":1,"external_direct_body_calls":20,"indirect_body_calls":4,"direct_bl_entry_sites":85,"stored_entry_pointers":0},"provider_boundary":{"easylogger_calls":10,"iar_dlib_calls":6,"first_party_parser_calls":4,"new_version_discriminator":False},"production":_validate_production()}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
