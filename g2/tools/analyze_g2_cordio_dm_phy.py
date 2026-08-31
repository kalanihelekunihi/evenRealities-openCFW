#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio PHY manager."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]; IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"; LOAD_BASE=0x437FE0
sys.path.insert(0,str(ROOT/"tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE_BYTES=3_523_396; IMAGE_SHA256="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
ARCHIVE=ROOT/"research/readiness/dm-phy/SHA256SUMS"; ARCHIVE_BYTES=1208; ARCHIVE_SHA="0af0ef1de07b5189dac92dba35eb27a948266a1098d3060326f64a360fc92eab"
CONFIG=ROOT/"components/apollo_main/core_overlay/overlay.json"; REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json"; MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
SOURCE=ROOT/"components/shared/cordio/runtime_cordio_dm_phy.c"; HEADER=ROOT/"components/shared/cordio/runtime_cordio_dm_phy.h"; TEST=ROOT/"tests/test_runtime_cordio_dm_phy.py"
PACKAGE=ROOT/"build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"; FLASH_PLAN=ROOT/"build/source/flash-plan.json"
SOURCE_PIN=(6206,"053d5e876a6a770d6c8923b1f89e7080c6b835df6fa7f63a5d73316393b99bfe"); HEADER_PIN=(3745,"04cdb49c415ffd76c2f22bd99c42995a0870851aa07d9915f8fcbc398a4779eb"); TEST_PIN=(7334,"6d5c0edaa780052fb1019cbeb7bacb4bac3bc1ee16b1dcdbdc9d1863773124d5")
PINS={ROOT/"tools/manifests/packetcraft-cordio-dm-phy-function-map.tsv":"b5c106d895fe304d6145cd5f4e70ae3e1b6974af99d001995bd7bffaedb542fd",ROOT/"tools/manifests/packetcraft-cordio-dm-phy-provenance.tsv":"a0f79887862443ba56c4271286da45f73ac931c9961449d4a222d9f799b0aa7d",ROOT/"tools/manifests/readiness-cordio-dm-phy-build-results.tsv":"20977d4ce2f8dd3fc819019c29ec6bbd45b66ac3cb069c19cd78cad48984f05e",ROOT/"tools/manifests/readiness-cordio-dm-phy-closure-results.tsv":"b8b5de3a8b996d30cabb5ce7978acdc936210d898cd8fb94789f05d1aba7a352",ROOT/"tools/manifests/readiness-cordio-dm-phy-source-identities.tsv":"3b5ad347d4116a2c8d6eaecb60421061abfc9a8dfc7f7349c141e482a7115d3a",ROOT/"tools/manifests/readiness-cordio-dm-phy-undefined-providers.tsv":"dd32650710e197fbb4eb93018c3e64c4e0b171270120df005118538c329e7804"}
FUNCS={"dmPhyHciHandler":(0x4C5734,0x4C5774,"9e40baefe98da28f8e0cc417551867ff9eeaa2337bc91bad9287486bb920d82c"),"dmPhyActPhyRead":(0x4C5774,0x4C57AE,"d4276c9deab89d4a0f0a00a0a3a055d3c8abbbcafb2f28c5a01a1f89961ba5af"),"dmPhyActDefPhySet":(0x4C57AE,0x4C57D6,"b71ff76b3d1ac7de8e9fd4b43f2d9e322eb52a8364b59f6d97f2169140d15bd9"),"dmPhyActPhyUpdate":(0x4C57D6,0x4C5810,"d96ccb215e22511198a90d8832be644907fac11d1bc86185b5399f30e49d2dde"),"DmSetPhy":(0x4C5810,0x4C584A,"b385682ac5aa3d223d606c005d9e17884ab882250d3628476b46eefaf0bf631f"),"DmPhyInit":(0x4C584A,0x4C5868,"bc066ea467f1886fceb6ff6a2dd6db47e40bf38fc90827b128debfe5efc82197")}
CALLERS={"dmPhyHciHandler":[],"dmPhyActPhyRead":[0x4C5762],"dmPhyActDefPhySet":[0x4C5740],"dmPhyActPhyUpdate":[0x4C576C],"DmSetPhy":[0x472626],"DmPhyInit":[0x4B8016]}
PRODUCTION_FUNCTIONS=["open_cfw_cordio_dm_phy_hci_handler","open_cfw_cordio_dm_phy_action_read","open_cfw_cordio_dm_phy_action_default","open_cfw_cordio_dm_phy_action_update","open_cfw_cordio_dm_phy_set","open_cfw_cordio_dm_phy_initialize"]
PRODUCTION_LEAVES=[(289460,62,4,"c05b23d970e9dd86f5cd3c4b12951dae0c50f945df75e5d2196a740501442036"),(289524,80,0,"5d6be7ce5bb96da245a9ee876c7ceb65d06cda0de814a649b8bc04fde3205993"),(289604,56,0,"ec1677a280ab56f167892232dcf516ea16ebaa7ecde544775c3272aa0b8a34da"),(289660,80,0,"b9a548fbc85c5714330d612457c7d8f8028b7913528c99e32d30c1b83aedee8b"),(289740,56,4,"09e3173b9da5dfd46f0c6b8ad621cbbffe4f416721086f4203f8125b3e9a26e1"),(289796,44,3,"63d9ac5d1229cca99221992d888c4b3afc9e8cb3653cfd16f5fef6fcfe895295")]
def sha(d): return hashlib.sha256(d).hexdigest()
def sl(b,s,e): return b[s-LOAD_BASE:e-LOAD_BASE]
def decoder():
 tools=str(ROOT/"tools")
 if tools not in sys.path: sys.path.insert(0,tools)
 p=ROOT/"tools/recover_apollo_embedded_source_paths.py"; spec=importlib.util.spec_from_file_location("dm_phy_thumb",p); assert spec and spec.loader; m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
def verify_file(path,expected,label):
 d=path.read_bytes()
 if (len(d),sha(d))!=expected: raise RuntimeError(f"{label} changed")
def verify_production():
 verify_file(SOURCE,SOURCE_PIN,"dm_phy source");verify_file(HEADER,HEADER_PIN,"dm_phy header");verify_file(TEST,TEST_PIN,"dm_phy test")
 report=json.loads(REPORT.read_text());config=json.loads(CONFIG.read_text());manifest=json.loads(MANIFEST.read_text())
 leaves=sorted([r for r in report["relocated_leaves"] if r.get("source",{}).get("path","").endswith(SOURCE.name)],key=lambda r:r["pins"]["offset"])
 if len(leaves)!=6: raise RuntimeError("dm_phy production leaf count changed")
 for row,function,expected in zip(leaves,PRODUCTION_FUNCTIONS,PRODUCTION_LEAVES):
  observed=(row["pins"]["offset"],row["extraction"]["size"],row["extraction"]["relocation_count"],row["extraction"]["sha256"])
  if row["extraction"]["function"]!=function or observed!=expected: raise RuntimeError(f"dm_phy production leaf changed: {function}")
 sites={r["name"]:r for r in config["patch_sites"] if r["name"].startswith("replace_cordio_dm_phy_")}
 for index,((name,(start,end,digest)),function) in enumerate(zip(FUNCS.items(),PRODUCTION_FUNCTIONS),1):
  site=sites.get(f"replace_cordio_dm_phy_{index:02d}")
  if site is None or site["runtime_address"]!=start or site["expected_size"]!=end-start or site["expected_sha256"]!=digest or site["target_function"]!=function or site["branch"]!="b_w": raise RuntimeError(f"dm_phy production route changed: {name}")
 override=manifest["component_overrides"]["apollo_main"];regions=[r for r in override["regions"] if r["name"].startswith("cordio_dm_phy_")]
 validate_apollo_main_artifacts(ROOT,RuntimeError,"Cordio DM PHY")
 if len(regions)!=14: raise RuntimeError("dm_phy component ownership changed")
 flash=json.loads(FLASH_PLAN.read_text());counts=tuple(len(flash[k]) for k in ("flash_regions","unresolved_flash_regions","container_only_regions","protected_regions"))
 return {"status":"production-routed","redirected_stock_functions":6,"redirected_stock_bytes":308,"source_owned_bytes_added":sum(r[1] for r in PRODUCTION_LEAVES),"alignment_bytes_added":sum(r["placement"]["padding_before"] for r in leaves),"strict_relocations":sum(r[2] for r in PRODUCTION_LEAVES),"source_only_target_compiled":["DmReadPhy","DmSetDefaultPhy"],"manifest_regions":len(regions),"flash_plan_counts":counts}
def analyze(image:Path=IMAGE)->dict[str,Any]:
 b=image.read_bytes()
 if len(b)!=IMAGE_BYTES or sha(b)!=IMAGE_SHA256: raise RuntimeError("official image changed")
 if ARCHIVE.stat().st_size!=ARCHIVE_BYTES or sha(ARCHIVE.read_bytes())!=ARCHIVE_SHA: raise RuntimeError("dm_phy artifact changed")
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h: raise RuntimeError(f"pinned input changed: {p}")
 bodies=[]
 for n,(s,e,h) in FUNCS.items():
  d=sl(b,s,e)
  if sha(d)!=h: raise RuntimeError(f"body changed: {n}")
  bodies.append(d)
 if sha(b"".join(bodies))!="cdb83d68ae2c20170620e3c9f05059388d553e041ceaf6319edac85aee92cf4a" or sha(sl(b,0x4C5734,0x4C5874))!="3c0856787ff56af58207792e0d15365aae8de8efb84efb82e9398dd5c7cf81e8": raise RuntimeError("dm_phy interval changed")
 tail=sl(b,0x4C5868,0x4C5874); interface=sl(b,0x78A85C,0x78A868)
 if sha(tail)!="a2cee8d66ef23eadff455b1c38806cd1743c6957299025897b5b2119d3884c41" or list(struct.unpack("<3I",tail))!=[0x200712A4,0x78A85C,0x20000694]: raise RuntimeError("tail changed")
 if sha(interface)!="3794cf8786f7ac1d372238f121ca140d76466e0a6ec54a77f4bd250bcd7de2f3" or list(struct.unpack("<3I",interface))!=[0x4D29BF,0x4C5735,0x4D29C1]: raise RuntimeError("interface changed")
 dec=decoder(); starts={s:n for n,(s,_,_) in FUNCS.items()}; calls={n:[] for n in FUNCS}
 for a in range(LOAD_BASE,LOAD_BASE+len(b)-3,2):
  t=dec._thumb_bl_target(b,a)
  if t in starts:calls[starts[t]].append(a)
 if calls!=CALLERS: raise RuntimeError("caller closure changed")
 entries=set(starts); interiors=set(); stored={}; interior=[]
 for s,e,_ in FUNCS.values(): interiors.update(range(s+2,e,2))
 for a in range(LOAD_BASE,LOAD_BASE+len(b)-3,4):
  v=struct.unpack("<I",sl(b,a,a+4))[0]; t=v&~1
  if t in entries: stored[a]=v
  elif t in interiors: interior.append((a,v))
 if stored!={0x78A860:0x4C5735} or interior: raise RuntimeError("stored/interior ingress changed")
 return {"schema_version":1,"module":{"start":0x4C5734,"end_exclusive":0x4C5874,"physical_bytes":320,"linked_function_count":6,"linked_function_bytes":308,"source_inventory_functions":8,"source_only_functions":["DmReadPhy","DmSetDefaultPhy"],"direct_bl_ingress_sites":5,"registered_function_pointers":1,"strict_interior_pointers":0},"architecture":{"component_id":9,"hci_events":[41,42,43],"callback_events":[0x44,0x45,0x46],"widened_feature_mask":0x900,"widened_feature_mask_high":0,"feature_enable":True},"abi":{"dm_conn_cb":0x200712A4},"lineage":{"selected_blob":"50124b4c6381c744eefc241ede3888989b56897e","selected_sha256":"0bbe1687c0ababa185443a61aedab08037445d4802aaa8b6978f8a8d4f4a272c","license":"Apache-2.0","historical_generating_commit_resolved":False},"readiness":{"archive_sha256":ARCHIVE_SHA,"source_functions_built":8,"provider_seams":12,"valid_non_vacuous_closure_profiles":2,"linked_unresolved_symbols":0},"production":verify_production()}
def main():
 p=argparse.ArgumentParser(); p.add_argument("--image",type=Path,default=IMAGE); p.add_argument("--json",action="store_true"); a=p.parse_args(); r=analyze(a.image); print(json.dumps(r,indent=2,sort_keys=True) if a.json else "Cordio dm_phy closed: 6 linked / 2 source-only"); return 0
if __name__=="__main__": raise SystemExit(main())
