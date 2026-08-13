#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio master-security wrappers."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"; LOAD_BASE=0x437FE0
IMAGE_BYTES=3_523_396; IMAGE_SHA="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
ARCHIVE=ROOT/"research/readiness/dm-sec-master/SHA256SUMS"; ARCHIVE_BYTES=1288; ARCHIVE_SHA="0f47a4f15996dfceecedf9e29ad1f43e0816d159da2e8e6527ad21e3f55b3526"
PINS={ROOT/"tools/manifests/packetcraft-cordio-dm-sec-master-function-map.tsv":"f807609cd69bf43e6d418ac628af40bdb10fea18a3e951eed9ec5fc276e589ff",ROOT/"tools/manifests/packetcraft-cordio-dm-sec-master-provenance.tsv":"8c0c04ba0a27dbdb130bfeb84663d65617dfbc51fdf16fe464d9dcaf0e09d30c",ROOT/"tools/manifests/readiness-cordio-dm-sec-master-build-results.tsv":"7a09e71ab13fba9d06bcc306b72f9b305e1171a279ec6e660daf085a7ec81710",ROOT/"tools/manifests/readiness-cordio-dm-sec-master-closure-results.tsv":"18d0c101cbe79803c07bfdf8cc2087aeda174305b9b02d3c417bf4cf5ee50ace",ROOT/"tools/manifests/readiness-cordio-dm-sec-master-source-identities.tsv":"1c42ab3a3084b41417e7d7f1cdb31e55b0cf26b1d9489c4e92e675bf5df628ef",ROOT/"tools/manifests/readiness-cordio-dm-sec-master-undefined-providers.tsv":"1690dd4e4934c7d5842e8f273aa3decb2f2c0f5a499566825afb5bb70488cb4c"}
FUNCS={"DmSmpEncryptReq":(0x55BBC4,0x55BBEA,"878fbf663cc2445b7d03395bf9cb8ab7944658da6a7a8cffac71d70683cbd795"),"DmSecPairReq":(0x55BBEA,0x55BC1E,"e290734ff914383453ae27304f2bc1710cb86357808d8023ee16818e994578ad"),"DmSecEncryptReq":(0x55BC1E,0x55BC54,"cb65fa971d10bb1e237b38c5a69fa5de850cacd6d6a12ad171ebed98edaa94f7")}
CALLERS={"DmSmpEncryptReq":[0x5E3356,0x5E3854],"DmSecPairReq":[0x50353A],"DmSecEncryptReq":[0x5034C6]}
def sha(b):return hashlib.sha256(b).hexdigest()
def sl(b,s,e):return b[s-LOAD_BASE:e-LOAD_BASE]
def dec():
 tools=str(ROOT/"tools")
 if tools not in sys.path:sys.path.insert(0,tools)
 p=ROOT/"tools/recover_apollo_embedded_source_paths.py"; spec=importlib.util.spec_from_file_location("dm_sec_master_thumb",p); assert spec and spec.loader; m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
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
 if sha(b"".join(bodies))!="335ed66e12f8479d4555c7d34a6a57d3e483b707d747445337d57728a7d4ca85" or sha(sl(b,0x55BBC4,0x55BC5C))!="9e57f961ad2655c12eda32bb6d2fbb6c5a7e34b2588e3d399fb2ec77299bc43b":raise RuntimeError("interval changed")
 tail=sl(b,0x55BC54,0x55BC5C)
 if sha(tail)!="32810d82e7286a55ab4700be24e1bbbdb2a883663cf2b194ab50a3fd3e86170d" or list(struct.unpack("<2I",tail))!=[0x7856B0,0x20073B78]:raise RuntimeError("tail changed")
 m=dec(); starts={s:n for n,(s,_,_) in FUNCS.items()}; calls={n:[] for n in FUNCS}
 for a in range(LOAD_BASE,LOAD_BASE+len(b)-3,2):
  t=m._thumb_bl_target(b,a)
  if t in starts:calls[starts[t]].append(a)
 if calls!=CALLERS:raise RuntimeError("callers changed")
 interiors=set()
 for s,e,_ in FUNCS.values():interiors.update(range(s+2,e,2))
 for off in range(len(b)-3):
  t=struct.unpack_from("<I",b,off)[0]&~1
  if t in starts or t in interiors:raise RuntimeError("stored entry/interior pointer found")
 return {"schema_version":1,"module":{"start":0x55BBC4,"end_exclusive":0x55BC5C,"physical_bytes":152,"linked_function_count":3,"linked_function_bytes":144,"source_inventory_functions":3,"source_only_functions":[],"direct_bl_ingress_sites":4,"registered_function_pointers":0,"strict_interior_pointers":0},"architecture":{"encrypt_request_event":0x28,"message_id_shift":3},"abi":{"calc128_zeros":0x7856B0,"dm_cb":0x20073B78,"dm_sec_cb":0x20074114},"lineage":{"selected_blob":"a941ac7e6d4199d76e5cae0e157efcf8d16dfb64","selected_sha256":"4a17020e0f7076e81ea4878f3423569ecdfb7deaf6b7d8fcd753cd04926c9ffe","license":"Apache-2.0","historical_generating_commit_resolved":False},"readiness":{"archive_sha256":ARCHIVE_SHA,"source_functions_built":3,"provider_seams":8,"valid_non_vacuous_closure_profiles":2,"linked_unresolved_symbols":0},"production":{"stock_bytes_replaced":0,"source_owned_bytes_added":0}}
def main():
 p=argparse.ArgumentParser();p.add_argument("--image",type=Path,default=IMAGE);p.add_argument("--json",action="store_true");a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else "Cordio dm_sec_master closed: 3 linked / 0 source-only");return 0
if __name__=="__main__":raise SystemExit(main())
