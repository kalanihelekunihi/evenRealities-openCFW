#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio L2CAP master unit."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_BYTES=3_523_396;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
PINS={ROOT/'tools/manifests/packetcraft-cordio-l2c-master-function-map.tsv':'c0053ee3c8973deca350223a35b61af30dd1e0dde537b04a9411b29e2973a8ff',ROOT/'tools/manifests/packetcraft-cordio-l2c-master-provenance.tsv':'f9d20ef146068e506a8f379a78fb771936009266169dfae76e8596cec9bce5a7'}
SOURCE=ROOT/'components/shared/cordio/runtime_cordio_l2c_master.c'
SOURCE_SHA='a23f0afd51e158e6c27119bb6688477df1dd9a498f63f5c7a4245bbed52847db'
PRODUCTION_FUNCTIONS=['open_cfw_cordio_l2c_master_receive_signaling_packet','open_cfw_cordio_l2c_master_initialize','open_cfw_cordio_l2c_connection_update_response']
PRODUCTION_METRICS=[(353900,210,3),(354112,20,0),(354132,56,2)]
F={'l2cMasterRxSignalingPkt':(0x536FBC,0x5371FE,'02e5f34c1e77998116f93ee16041cbb95156c198530345aad39954315fb23d7c'),'L2cMasterInit':(0x537200,0x537208,'ba04b13c8945ffa29186bcf41a112e3e9d17f8e8246a6632fd89748b7c94c0cc'),'L2cDmConnUpdateRsp':(0x537230,0x537278,'25fdad45770fddd5f782df33745ca172a975d5c17c6ac68920e7fb0648854c4d')}
CALLS={'l2cMasterRxSignalingPkt':[],'L2cMasterInit':[0x4B8050],'L2cDmConnUpdateRsp':[0x5371E6,0x55BC88]}
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,s,e):return b[s-BASE:e-BASE]
def dec():
 sys.path.insert(0,str(ROOT/'tools'));p=ROOT/'tools/recover_apollo_embedded_source_paths.py';q=importlib.util.spec_from_file_location('l2c_master_thumb',p);m=importlib.util.module_from_spec(q);sys.modules[q.name]=m;q.loader.exec_module(m);return m
def analyze(image_path=IMAGE):
 b=image_path.read_bytes()
 if len(b)!=IMAGE_BYTES or sha(b)!=IMAGE_SHA:raise RuntimeError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise RuntimeError(f'pinned input changed: {p}')
 bodies=[]
 for n,(s,e,h) in F.items():
  d=sl(b,s,e)
  if sha(d)!=h:raise RuntimeError(f'body changed: {n}')
  bodies.append(d)
 if sha(b''.join(bodies))!='c3ccc8967953216678f27060d7b29e4fa11efedcce0089b269245c66241d53f0':raise RuntimeError('body concat changed')
 if sha(sl(b,0x536FBC,0x537278))!='1cdae8cc0feb879079330aad4ba53141ce701314d0be844fde9c61a2f90a9536':raise RuntimeError('physical object changed')
 if sha(sl(b,0x5371FE,0x537200))!='9f848444199784b2941a5ed0d417d18194bb94ffa059efe79d2b32450bd3b6c4' or sha(sl(b,0x537208,0x537230))!='c71afc6b77b65f8b7093d292b5841b549973fc1f0e54c8015da9a37af7d2869a':raise RuntimeError('inline data changed')
 m=dec();starts={s:n for n,(s,_,_) in F.items()};calls={n:[] for n in F}
 for a in range(BASE,BASE+len(b)-3,2):
  t=m._thumb_bl_target(b,a)
  if t in starts:calls[starts[t]].append(a)
 if calls!=CALLS:raise RuntimeError('direct ingress changed')
 interior=set()
 for s,e,_ in F.values():interior.update(range(s+2,e,2))
 ent=[];inside=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0];t=v&~1
  if t in starts:ent.append((BASE+o,v))
  elif t in interior:inside.append((BASE+o,v))
 if ent!=[(0x537228,0x536FBD)] or inside:raise RuntimeError('stored/interior ingress changed')
 from analyze_g2_cordio_l2c_production import validate
 production=validate(source=SOURCE,source_sha256=SOURCE_SHA,
  functions=PRODUCTION_FUNCTIONS,metrics=PRODUCTION_METRICS,
  patch_prefix='replace_cordio_l2c_master_',region_prefix='cordio_l2c_master_',
  stock_functions=F,stock_bytes=658,source_functions=3,source_only=[],
  region_count=7,hardening={'signaling_shape_and_parameter_ranges_hardened':True})
 return {'schema_version':1,'module':{'start':0x536FBC,'end_exclusive':0x537278,'physical_bytes':700,'linked_function_count':3,'linked_function_bytes':658,'source_inventory_functions':3,'source_only_functions':[],'direct_bl_ingress_sites':3,'registered_function_pointers':1,'strict_interior_pointers':0},'architecture':{'source_bodies_release_invariant':True,'master_receive_callback_cell':0x537228,'neighboring_dm_abi':'r20/R4'},'lineage':{'selected_blob':'0f6c8c0594c0cd877f9c4fe22e42ef656863bbc4','selected_sha256':'040a732f615345250d2cee7c8293c2e2c420b5bbaf264f65e7ec65117e0c0be3','license':'Apache-2.0','independent_release_discriminator':False},'build_readiness':{'status':'production-routed','reason':'host and isolated Cortex-M55 gates green'},'production':production}
def main():
 p=argparse.ArgumentParser();p.add_argument('--image',type=Path,default=IMAGE);p.add_argument('--json',action='store_true');a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else 'Cordio l2c_master closed: 3 linked');return 0
if __name__=='__main__':raise SystemExit(main())
