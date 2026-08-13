#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio master connection manager."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"; BASE=0x437FE0
IMAGE_BYTES=3_523_396; IMAGE_SHA="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
ARCHIVE=ROOT/"research/readiness/dm-conn-master/SHA256SUMS"; ARCHIVE_BYTES=1288; ARCHIVE_SHA="6612a0c946de552cbd0ca6cddbd9e7f39561d5cc6cb564900b67a0b011b4aee5"
PINS={ROOT/"tools/manifests/packetcraft-cordio-dm-conn-master-function-map.tsv":"e8add97b161a1d07ec1e2fbceda41d6da5c5be5df8ed062a20dd263f651eb2a3",ROOT/"tools/manifests/packetcraft-cordio-dm-conn-master-provenance.tsv":"caa6efcc407c6cb1ad74d3e08241aaedac2a5d8308a03978a0e9b3c67f076d6c",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-build-results.tsv":"cd7fa57e5fd3328e8d6b16f7a7726763912b77d5856492f62b83f03f4309ca60",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-closure-results.tsv":"a8926f872417f5c1b6fa7e18aba5daf4cca98fdba7fbd3e99d3e91d64dddc1cd",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-source-identities.tsv":"4dc462af90696bb83e7b93a0e3a1ff25949af7a42997c50dae342de34c8d84b4",ROOT/"tools/manifests/readiness-cordio-dm-conn-master-undefined-providers.tsv":"a9400292a362e01282c268f24efee891b98ea73c0d567bce8b6db48b8a5dd097"}
FUNCS={"dmConnSmActCancelOpen":(0x55BC5C,0x55BC70,"a23ea8944f1d0b6fd90addad55137495f65fef15ce2d335c9634aac78be729a4"),"dmConnUpdActUpdateMaster":(0x55BC70,0x55BC7C,"d20f869584455234758897ababdac7a6f9d8e3be9979ffb1c918b4d4dce80b62"),"dmConnUpdActL2cUpdateInd":(0x55BC7C,0x55BC96,"2091ac4ecd3e9c86bfa954cdd5bda8fe147fba3848c8b5c7fb734a9aeb6ce471"),"DmL2cConnUpdateInd":(0x55BC96,0x55BCC0,"1a51a92e695798d1499b45008e2b4d707066d891f13c222be8c3dbc7838ed97b"),"DmConnOpen":(0x55BCC0,0x55BCE6,"8beae94614b30307be34969ba1d2f9ba7c01c63fdd5bd6f8281560b8de8e31ed")}
CALLERS={"dmConnSmActCancelOpen":[],"dmConnUpdActUpdateMaster":[],"dmConnUpdActL2cUpdateInd":[],"DmL2cConnUpdateInd":[0x5371F6],"DmConnOpen":[0x503D34]}
def sha(b):return hashlib.sha256(b).hexdigest()
def sl(b,s,e):return b[s-BASE:e-BASE]
def decoder():
 tools=str(ROOT/"tools")
 if tools not in sys.path:sys.path.insert(0,tools)
 p=ROOT/"tools/recover_apollo_embedded_source_paths.py";s=importlib.util.spec_from_file_location("dm_conn_master_thumb",p);assert s and s.loader;m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
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
 return {"schema_version":1,"module":{"start":0x55BC5C,"end_exclusive":0x55BCE8,"physical_bytes":140,"linked_function_count":5,"linked_function_bytes":138,"source_inventory_functions":6,"source_only_functions":["DmConnSetAddrType"],"direct_bl_ingress_sites":2,"registered_function_pointers":3,"strict_interior_pointers":0},"architecture":{"connection_update_component_id":14,"l2c_update_event":0x72,"separate_update_executor":True,"update_action_entries":2},"lineage":{"selected_blob":"d92f3e7ee4f64b27799337fb421198fda14f55a3","selected_sha256":"8555ab595045465c0ae6ef018a5af41d9003fd40e942e4b69ef42eb326a02ca0","license":"Apache-2.0","historical_generating_commit_resolved":False},"readiness":{"archive_sha256":ARCHIVE_SHA,"source_functions_built":6,"provider_seams":10,"valid_non_vacuous_closure_profiles":2,"linked_unresolved_symbols":0},"production":{"stock_bytes_replaced":0,"source_owned_bytes_added":0}}
def main():
 p=argparse.ArgumentParser();p.add_argument("--image",type=Path,default=IMAGE);p.add_argument("--json",action="store_true");a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else "Cordio dm_conn_master closed: 5 linked / 1 source-only");return 0
if __name__=="__main__":raise SystemExit(main())
