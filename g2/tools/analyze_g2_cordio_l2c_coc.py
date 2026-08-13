#!/usr/bin/env python3
"""Fail-closed exclusion audit for optional Cordio L2CAP CoC on stock G2."""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_BYTES=3_523_396;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/packetcraft-cordio-l2c-coc-function-map.tsv';PV=ROOT/'tools/manifests/packetcraft-cordio-l2c-coc-provenance.tsv'
PINS={FM:'44551a842fa0340f1f1528f05a94efda9b549459f2c7d69d5f3ee1240d163ba3',PV:'f6269f9537fa7fe41e7aa8d67bd86bd424fceeb634783075d56ef95cb8f1e9c1'}
L2C_CB=0x200737D8;L2C_CB_CELLS=[0x530B90,0x536FA0,0x53722C];DM_CONN_REGISTER=0x4B6C64;DM_REGISTER_CALLERS=[0x4B5140,0x4B7ED2,0x537CF2]
INIT_SPANS={(0x530B34,0x530B5E):'cb21c7a5d22c959e24d20e4242a34160cec9fb326fbd6320d9efb36f0aba4bff',(0x536E78,0x536E9A):'dcad41f54cb73ecbe50266f95706a8da707309c9359979891d2953af3ce07e99',(0x537200,0x537208):'ba04b13c8945ffa29186bcf41a112e3e9d17f8e8246a6632fd89748b7c94c0cc'}
ABSENT=(b'l2c_coc.c',b'l2cCoc',b'L2cCoc',b'l2cRegCbAlloc',b'l2cChanCbAlloc')
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,s,e):return b[s-BASE:e-BASE]
def dec():
 sys.path.insert(0,str(ROOT/'tools'));p=ROOT/'tools/recover_apollo_embedded_source_paths.py';q=importlib.util.spec_from_file_location('l2c_coc_thumb',p);m=importlib.util.module_from_spec(q);sys.modules[q.name]=m;q.loader.exec_module(m);return m
def occ(b,v):
 p=struct.pack('<I',v);return [BASE+i for i in range(len(b)-3) if b[i:i+4]==p]
def analyze(image_path=IMAGE):
 b=image_path.read_bytes()
 if len(b)!=IMAGE_BYTES or sha(b)!=IMAGE_SHA:raise RuntimeError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise RuntimeError(f'pinned input changed: {p}')
 with FM.open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
 if len(rows)!=67 or any(r['stock_status']!='dead_stripped' or r['stock_address']!='-' for r in rows):raise RuntimeError('source inventory changed')
 if occ(b,L2C_CB)!=L2C_CB_CELLS:raise RuntimeError('l2cCb reference closure changed')
 for bounds,h in INIT_SPANS.items():
  if sha(sl(b,*bounds))!=h:raise RuntimeError(f'neighbor initializer changed at {bounds[0]:#x}')
 for needle in ABSENT:
  if needle in b:raise RuntimeError(f'unexpected CoC marker appeared: {needle!r}')
 m=dec();calls=[]
 for a in range(BASE,BASE+len(b)-3,2):
  if m._thumb_bl_target(b,a)==DM_CONN_REGISTER:calls.append(a)
 if calls!=DM_REGISTER_CALLERS:raise RuntimeError('DmConnRegister caller closure changed')
 return {'schema_version':1,'module':{'classification':'not_linked_or_dead_stripped','linked_function_count':0,'linked_function_bytes':0,'source_inventory_functions':67,'source_only_functions':[r['function'] for r in rows],'retained_path_anchors':0,'semantic_body_anchors':0},'exclusion':{'l2c_control_block':L2C_CB,'l2c_control_block_literal_cells':L2C_CB_CELLS,'dm_conn_register_callers':calls,'coc_initializers':0,'retained_coc_markers':0,'mandatory_init_contract':'L2cCocInit must replace three l2cCb callbacks and call DmConnRegister'},'lineage':{'selected_optional_blob':'f78873f1435e1f4298c9e22b5114b7061f0d1e9c','selected_optional_sha256':'d6d41daaccc204cc9b4da200d9baf0f5004dfc7ef57690c47fb2526d7722ffb6','license':'Apache-2.0','stock_body_version_discriminated':False,'compatibility_basis':'surrounding proven r20 L2CAP/DM ABI'},'build_readiness':{'status':'deferred','reason':'optional TU absent; reverse engineering prioritized'},'production':{'stock_bytes_replaced':0,'source_owned_bytes_added':0}}
def main():
 p=argparse.ArgumentParser();p.add_argument('--image',type=Path,default=IMAGE);p.add_argument('--json',action='store_true');a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else 'Cordio l2c_coc excluded: 67 source-only');return 0
if __name__=='__main__':raise SystemExit(main())
