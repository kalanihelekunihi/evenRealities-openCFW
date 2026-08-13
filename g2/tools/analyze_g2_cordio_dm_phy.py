#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio PHY manager."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]; IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"; LOAD_BASE=0x437FE0
IMAGE_BYTES=3_523_396; IMAGE_SHA256="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
ARCHIVE=ROOT/"research/readiness/dm-phy/SHA256SUMS"; ARCHIVE_BYTES=1208; ARCHIVE_SHA="0af0ef1de07b5189dac92dba35eb27a948266a1098d3060326f64a360fc92eab"
PINS={ROOT/"tools/manifests/packetcraft-cordio-dm-phy-function-map.tsv":"b5c106d895fe304d6145cd5f4e70ae3e1b6974af99d001995bd7bffaedb542fd",ROOT/"tools/manifests/packetcraft-cordio-dm-phy-provenance.tsv":"a0f79887862443ba56c4271286da45f73ac931c9961449d4a222d9f799b0aa7d",ROOT/"tools/manifests/readiness-cordio-dm-phy-build-results.tsv":"20977d4ce2f8dd3fc819019c29ec6bbd45b66ac3cb069c19cd78cad48984f05e",ROOT/"tools/manifests/readiness-cordio-dm-phy-closure-results.tsv":"b8b5de3a8b996d30cabb5ce7978acdc936210d898cd8fb94789f05d1aba7a352",ROOT/"tools/manifests/readiness-cordio-dm-phy-source-identities.tsv":"3b5ad347d4116a2c8d6eaecb60421061abfc9a8dfc7f7349c141e482a7115d3a",ROOT/"tools/manifests/readiness-cordio-dm-phy-undefined-providers.tsv":"dd32650710e197fbb4eb93018c3e64c4e0b171270120df005118538c329e7804"}
FUNCS={"dmPhyHciHandler":(0x4C5734,0x4C5774,"9e40baefe98da28f8e0cc417551867ff9eeaa2337bc91bad9287486bb920d82c"),"dmPhyActPhyRead":(0x4C5774,0x4C57AE,"d4276c9deab89d4a0f0a00a0a3a055d3c8abbbcafb2f28c5a01a1f89961ba5af"),"dmPhyActDefPhySet":(0x4C57AE,0x4C57D6,"b71ff76b3d1ac7de8e9fd4b43f2d9e322eb52a8364b59f6d97f2169140d15bd9"),"dmPhyActPhyUpdate":(0x4C57D6,0x4C5810,"d96ccb215e22511198a90d8832be644907fac11d1bc86185b5399f30e49d2dde"),"DmSetPhy":(0x4C5810,0x4C584A,"b385682ac5aa3d223d606c005d9e17884ab882250d3628476b46eefaf0bf631f"),"DmPhyInit":(0x4C584A,0x4C5868,"bc066ea467f1886fceb6ff6a2dd6db47e40bf38fc90827b128debfe5efc82197")}
CALLERS={"dmPhyHciHandler":[],"dmPhyActPhyRead":[0x4C5762],"dmPhyActDefPhySet":[0x4C5740],"dmPhyActPhyUpdate":[0x4C576C],"DmSetPhy":[0x472626],"DmPhyInit":[0x4B8016]}
def sha(d): return hashlib.sha256(d).hexdigest()
def sl(b,s,e): return b[s-LOAD_BASE:e-LOAD_BASE]
def decoder():
 tools=str(ROOT/"tools")
 if tools not in sys.path: sys.path.insert(0,tools)
 p=ROOT/"tools/recover_apollo_embedded_source_paths.py"; spec=importlib.util.spec_from_file_location("dm_phy_thumb",p); assert spec and spec.loader; m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
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
 return {"schema_version":1,"module":{"start":0x4C5734,"end_exclusive":0x4C5874,"physical_bytes":320,"linked_function_count":6,"linked_function_bytes":308,"source_inventory_functions":8,"source_only_functions":["DmReadPhy","DmSetDefaultPhy"],"direct_bl_ingress_sites":5,"registered_function_pointers":1,"strict_interior_pointers":0},"architecture":{"component_id":9,"hci_events":[41,42,43],"callback_events":[0x44,0x45,0x46],"widened_feature_mask":0x900,"widened_feature_mask_high":0,"feature_enable":True},"abi":{"dm_conn_cb":0x200712A4},"lineage":{"selected_blob":"50124b4c6381c744eefc241ede3888989b56897e","selected_sha256":"0bbe1687c0ababa185443a61aedab08037445d4802aaa8b6978f8a8d4f4a272c","license":"Apache-2.0","historical_generating_commit_resolved":False},"readiness":{"archive_sha256":ARCHIVE_SHA,"source_functions_built":8,"provider_seams":12,"valid_non_vacuous_closure_profiles":2,"linked_unresolved_symbols":0},"production":{"stock_bytes_replaced":0,"source_owned_bytes_added":0}}
def main():
 p=argparse.ArgumentParser(); p.add_argument("--image",type=Path,default=IMAGE); p.add_argument("--json",action="store_true"); a=p.parse_args(); r=analyze(a.image); print(json.dumps(r,indent=2,sort_keys=True) if a.json else "Cordio dm_phy closed: 6 linked / 2 source-only"); return 0
if __name__=="__main__": raise SystemExit(main())
