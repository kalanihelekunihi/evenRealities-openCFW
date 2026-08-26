#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio master connection manager."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"; BASE=0x437FE0
IMAGE_BYTES=3_523_396; IMAGE_SHA="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
CONFIG=ROOT/"components/apollo_main/core_overlay/overlay.json";REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
SOURCE=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_master.c";HEADER=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_master.h";TEST=ROOT/"tests/test_runtime_cordio_dm_conn_master.py";PACKAGE=ROOT/"build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin";FLASH_PLAN=ROOT/"build/source/flash-plan.json"
SOURCE_PIN=(3641,"c6391cfc005a08447a1ed8d7ca49eead69a2683686ac69ad50f4a75c929c1991");HEADER_PIN=(2151,"8bc4f52f625db653fa664b0a609d19bcf5f8cf59f4f7a9a434f5a8f6ebf28fdf");TEST_PIN=(3953,"9a8c75480c1f0af609dd07bde66eac7a114dfc3d3e76c5ffa1743c95c4c8553c")
PRODUCTION_OVERLAY=(404796,"a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d");PRODUCTION_COMPONENT=(3928192,"5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73");PRODUCTION_PACKAGE=(4706686,"30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf");PRODUCTION_FLASH_PLAN=(4071097,"cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d")
ARCHIVE=ROOT/"research/readiness/dm-conn-master/SHA256SUMS"; ARCHIVE_BYTES=1288; ARCHIVE_SHA="6612a0c946de552cbd0ca6cddbd9e7f39561d5cc6cb564900b67a0b011b4aee5"
PINS={ROOT/"tools/manifests/packetcraft-cordio-dm-conn-master-function-map.tsv":"e8add97b161a1d07ec1e2fbceda41d6da5c5be5df8ed062a20dd263f651eb2a3",ROOT/"tools/manifests/packetcraft-cordio-dm-conn-master-provenance.tsv":"caa6efcc407c6cb1ad74d3e08241aaedac2a5d8308a03978a0e9b3c67f076d6c",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-build-results.tsv":"cd7fa57e5fd3328e8d6b16f7a7726763912b77d5856492f62b83f03f4309ca60",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-closure-results.tsv":"a8926f872417f5c1b6fa7e18aba5daf4cca98fdba7fbd3e99d3e91d64dddc1cd",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-source-identities.tsv":"4dc462af90696bb83e7b93a0e3a1ff25949af7a42997c50dae342de34c8d84b4",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-undefined-providers.tsv":"a9400292a362e01282c268f24efee891b98ea73c0d567bce8b6db48b8a5dd097"}
FUNCS={"dmConnSmActCancelOpen":(0x55BC5C,0x55BC70,"a23ea8944f1d0b6fd90addad55137495f65fef15ce2d335c9634aac78be729a4"),"dmConnUpdActUpdateMaster":(0x55BC70,0x55BC7C,"d20f869584455234758897ababdac7a6f9d8e3be9979ffb1c918b4d4dce80b62"),"dmConnUpdActL2cUpdateInd":(0x55BC7C,0x55BC96,"2091ac4ecd3e9c86bfa954cdd5bda8fe147fba3848c8b5c7fb734a9aeb6ce471"),"DmL2cConnUpdateInd":(0x55BC96,0x55BCC0,"1a51a92e695798d1499b45008e2b4d707066d891f13c222be8c3dbc7838ed97b"),"DmConnOpen":(0x55BCC0,0x55BCE6,"8beae94614b30307be34969ba1d2f9ba7c01c63fdd5bd6f8281560b8de8e31ed")}
CALLERS={"dmConnSmActCancelOpen":[],"dmConnUpdActUpdateMaster":[],"dmConnUpdActL2cUpdateInd":[],"DmL2cConnUpdateInd":[0x5371F6],"DmConnOpen":[0x503D34]}
PRODUCTION_FUNCTIONS=["open_cfw_cordio_dm_connection_master_action_cancel","open_cfw_cordio_dm_connection_master_action_update","open_cfw_cordio_dm_connection_master_action_l2c_indication","open_cfw_cordio_dm_connection_master_l2c_indication","open_cfw_cordio_dm_connection_master_open"]
PRODUCTION_LEAVES=[(358924,22,2,"9a00673c1c3d865de444211f16b385ebb31c582c59a2881ca21535bc9e04f677"),(358948,16,1,"2b395de286dc7e99bf262126a0addc3bb9100ccb25034751e7e9872c25aad6d0"),(358964,92,2,"971a1e7f3c5692fefbc61e589b670eca9d4194a3779bdb0a9545f78d645084a7"),(359056,52,2,"9b6f754335e55e87fc61bbe4ecfad4c5aec2cd5877456eaf4679fea217a63201"),(359108,38,1,"04aa1bd0abb4729720cd7b200fe0ed19dc9fcf457bb4b4505d7c675a2307d452")]
def sha(b):return hashlib.sha256(b).hexdigest()
def sl(b,s,e):return b[s-BASE:e-BASE]
def decoder():
 tools=str(ROOT/"tools")
 if tools not in sys.path:sys.path.insert(0,tools)
 p=ROOT/"tools/recover_apollo_embedded_source_paths.py";s=importlib.util.spec_from_file_location("dm_conn_master_thumb",p);assert s and s.loader;m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def verify_file(p,e,l):
 d=p.read_bytes()
 if (len(d),sha(d))!=e:raise RuntimeError(f"{l} changed")
def verify_production():
 verify_file(SOURCE,SOURCE_PIN,"master source");verify_file(HEADER,HEADER_PIN,"master header");verify_file(TEST,TEST_PIN,"master test");r=json.loads(REPORT.read_text());c=json.loads(CONFIG.read_text());m=json.loads(MANIFEST.read_text());leaves=sorted([x for x in r["relocated_leaves"] if x.get("source",{}).get("path","").endswith(SOURCE.name)],key=lambda x:x["pins"]["offset"])
 if len(leaves)!=5:raise RuntimeError("master leaf count changed")
 for x,f,e in zip(leaves,PRODUCTION_FUNCTIONS,PRODUCTION_LEAVES):
  o=(x["pins"]["offset"],x["extraction"]["size"],x["extraction"]["relocation_count"],x["extraction"]["sha256"])
  if x["extraction"]["function"]!=f or o!=e:raise RuntimeError(f"master leaf changed: {f}")
 sites={x["name"]:x for x in c["patch_sites"] if x["name"].startswith("replace_cordio_dm_conn_master_core_")}
 for i,((n,(s,e,h)),f) in enumerate(zip(FUNCS.items(),PRODUCTION_FUNCTIONS),1):
  x=sites.get(f"replace_cordio_dm_conn_master_core_{i:02d}")
  if x is None or x["runtime_address"]!=s or x["expected_size"]!=e-s or x["expected_sha256"]!=h or x["target_function"]!=f or x["branch"]!="b_w":raise RuntimeError(f"master route changed: {n}")
 o=m["component_overrides"]["apollo_main"];regions=[x for x in o["regions"] if x["name"].startswith("cordio_dm_conn_master_core_")]
 if (r["overlay"]["size"],r["overlay"]["sha256"])!=PRODUCTION_OVERLAY or (r["component"]["size"],r["component"]["sha256"])!=PRODUCTION_COMPONENT or (o["provider"].get("size"),o["provider"].get("sha256"))!=PRODUCTION_COMPONENT or len(regions)!=11:raise RuntimeError("master ownership changed")
 verify_file(PACKAGE,PRODUCTION_PACKAGE,"master package");verify_file(FLASH_PLAN,PRODUCTION_FLASH_PLAN,"master flash plan");f=json.loads(FLASH_PLAN.read_text());counts=tuple(len(f[k]) for k in ("flash_regions","unresolved_flash_regions","container_only_regions","protected_regions"))
 if counts!=(5576,2,5,6):raise RuntimeError("master flash counts changed")
 return {"status":"production-routed","redirected_stock_functions":5,"redirected_stock_bytes":138,"source_owned_bytes_added":220,"alignment_bytes_added":2,"strict_relocations":8,"manifest_regions":11,"flash_plan_counts":counts}
def analyze(image_path:Path=IMAGE):
 b=image_path.read_bytes()
 if len(b)!=IMAGE_BYTES or sha(b)!=IMAGE_SHA:raise RuntimeError("official image changed")
 if ARCHIVE.stat().st_size!=ARCHIVE_BYTES or sha(ARCHIVE.read_bytes())!=ARCHIVE_SHA:raise RuntimeError("artifact changed")
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise RuntimeError(f"pin changed: {p}")
 bodies=[]
 for n,(s,e,h) in FUNCS.items():
  d=sl(b,s,e)
  if sha(d)!=h:raise RuntimeError(f"body changed: {n}")
  bodies.append(d)
 if sha(b"".join(bodies))!="0ba4f01642d7acac6397a0fb7a317c91873b6e536f51aacde7192c0da432b957" or sha(sl(b,0x55BC5C,0x55BCE8))!="f894567b3ff7e8656db0f7aa655f7d200039dd54d4e4e57eb3be48e559b99940":raise RuntimeError("interval changed")
 table=sl(b,0x78D41C,0x78D424);leg=sl(b,0x78D424,0x78D42C)
 if sha(table)!="2e09ae0bb88caae24d3c82a9f6dc43f556582c9598102685b23b746fde39e6e7" or list(struct.unpack("<2I",table))!=[0x55BC71,0x55BC7D]:raise RuntimeError("update table changed")
 if sha(leg)!="a85c4b893594c464c53639adaa8128a8e6207ceaaf4a532c0c57d3e6b4628268" or struct.unpack("<I",leg[4:])[0]!=0x55BC5D:raise RuntimeError("master action table changed")
 m=decoder();starts={s:n for n,(s,_,_) in FUNCS.items()};calls={n:[] for n in FUNCS}
 for a in range(BASE,BASE+len(b)-3,2):
  t=m._thumb_bl_target(b,a)
  if t in starts:calls[starts[t]].append(a)
 if calls!=CALLERS:raise RuntimeError("call closure changed")
 interiors=set()
 for s,e,_ in FUNCS.values():interiors.update(range(s+2,e,2))
 stored=[];inside=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];t=v&~1
  if t in starts:stored.append((BASE+off,v))
  elif t in interiors:inside.append((BASE+off,v))
 if stored!=[(0x78D41C,0x55BC71),(0x78D420,0x55BC7D),(0x78D428,0x55BC5D)] or inside:raise RuntimeError("stored/interior ingress changed")
 return {"schema_version":1,"module":{"start":0x55BC5C,"end_exclusive":0x55BCE8,"physical_bytes":140,"linked_function_count":5,"linked_function_bytes":138,"source_inventory_functions":6,"source_only_functions":["DmConnSetAddrType"],"direct_bl_ingress_sites":2,"registered_function_pointers":3,"strict_interior_pointers":0},"architecture":{"connection_update_component_id":14,"l2c_update_event":0x72,"separate_update_executor":True,"update_action_entries":2},"lineage":{"selected_blob":"d92f3e7ee4f64b27799337fb421198fda14f55a3","selected_sha256":"8555ab595045465c0ae6ef018a5af41d9003fd40e942e4b69ef42eb326a02ca0","license":"Apache-2.0","historical_generating_commit_resolved":False},"readiness":{"archive_sha256":ARCHIVE_SHA,"source_functions_built":6,"target_profiles":7,"provider_seams":10,"valid_non_vacuous_closure_profiles":2,"linked_unresolved_symbols":0},"production":verify_production()}
def main():
 p=argparse.ArgumentParser();p.add_argument("--image",type=Path,default=IMAGE);p.add_argument("--json",action="store_true");a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else "Cordio dm_conn_master closed: 5 linked / 1 source-only");return 0
if __name__=="__main__":raise SystemExit(main())
