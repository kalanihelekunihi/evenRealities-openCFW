#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio L2CAP slave unit."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'; BASE=0x437FE0
IMAGE_BYTES=3_523_396; IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
PINS={ROOT/'tools/manifests/packetcraft-cordio-l2c-slave-function-map.tsv':'214f6cb1e7d4bc4cf6d0e45022be5567b28e3978c67129f574caebbaef188183',ROOT/'tools/manifests/packetcraft-cordio-l2c-slave-provenance.tsv':'2ed1a9379e91071ed977a20d69922d49b16a3142b92ee441d1bade6d272da912'}
SOURCE=ROOT/'components/shared/cordio/runtime_cordio_l2c_slave.c'
SOURCE_SHA='5c42b0e55ce979d1c2c9d3294c98cb36854fd18c0519a33d3cda28637bfdf1c4'
PRODUCTION_FUNCTIONS=['open_cfw_cordio_l2c_slave_request_timeout','open_cfw_cordio_l2c_slave_receive_signaling_packet','open_cfw_cordio_l2c_slave_initialize','open_cfw_cordio_l2c_connection_update_request','open_cfw_cordio_l2c_slave_handler_initialize','open_cfw_cordio_l2c_slave_handler']
PRODUCTION_METRICS=[(285708,46,2),(285756,188,5),(285944,42,0),(285988,182,4),(286172,18,0),(286192,20,1)]
F={
'l2cSlaveReqTimeout':(0x536B40,0x536C52,'6a92ad3b7511c9cf56fde9b6c92642aa343da2f5a77dd3f66d49cca183aae63f'),
'l2cSlaveRxSignalingPkt':(0x536C5C,0x536E76,'dae4e51ce13fe94e7fa40c5d37fee245625df51fb4cfe5d5ec9734b5530bb9f1'),
'L2cSlaveInit':(0x536E78,0x536E9A,'dcad41f54cb73ecbe50266f95706a8da707309c9359979891d2953af3ce07e99'),
'L2cDmConnUpdateReq':(0x536EA4,0x536F6A,'c40c901ad0f7b6b7fcdaed74fcb7437de5ed6edcdbacb114992ec4188702a9e0'),
'L2cSlaveHandlerInit':(0x536F6A,0x536F76,'5fd69d43ef6952c910459e6d8b84418e2a5aab6e8fa36cb35c3ba0cb174e045c'),
'L2cSlaveHandler':(0x536FA4,0x536FBA,'f3d6f5750e866aa1a660e6b8090e1b0677bb3bd73af001e028ad1a240594d7b6')}
CALLS={'l2cSlaveReqTimeout':[0x536FB2],'l2cSlaveRxSignalingPkt':[],'L2cSlaveInit':[0x4B804C],'L2cDmConnUpdateReq':[0x56E554],'L2cSlaveHandlerInit':[0x4B8044],'L2cSlaveHandler':[]}
def sha(x): return hashlib.sha256(x).hexdigest()
def sl(b,s,e): return b[s-BASE:e-BASE]
def dec():
 sys.path.insert(0,str(ROOT/'tools')); p=ROOT/'tools/recover_apollo_embedded_source_paths.py'; q=importlib.util.spec_from_file_location('l2c_slave_thumb',p); m=importlib.util.module_from_spec(q); sys.modules[q.name]=m; q.loader.exec_module(m); return m
def analyze(image_path=IMAGE):
 b=image_path.read_bytes()
 if len(b)!=IMAGE_BYTES or sha(b)!=IMAGE_SHA: raise RuntimeError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h: raise RuntimeError(f'pinned input changed: {p}')
 bodies=[]
 for n,(s,e,h) in F.items():
  d=sl(b,s,e)
  if sha(d)!=h: raise RuntimeError(f'body changed: {n}')
  bodies.append(d)
 if sha(b''.join(bodies))!='b9308327c067aa287e1b54ff3a543965f6d72d41d92bdd5adbe4a57d2cd3cc1a': raise RuntimeError('body concat changed')
 if sha(sl(b,0x536B40,0x536FBC))!='30c891402f75994a7da4fb6457a4e4f6738ddb49a85e2eb7896fdf839d089bc1': raise RuntimeError('physical object changed')
 gaps=[(0x536C52,0x536C5C,'bc42552b5731aa7df17691a17679f506ebd2d33fe74cd2426fc2b50797258976'),(0x536E76,0x536E78,'9f848444199784b2941a5ed0d417d18194bb94ffa059efe79d2b32450bd3b6c4'),(0x536E9A,0x536EA4,'19b5846d236e63a2f19649c8d0d4d3161fd0fde0087143a51aa808f15bfc43de'),(0x536F76,0x536FA4,'b29da9f41c981722e13822b9ba22362d7dff12077f439aaecd667cba4f56dcde'),(0x536FBA,0x536FBC,'96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7')]
 for s,e,h in gaps:
  if sha(sl(b,s,e))!=h: raise RuntimeError('inline data changed')
 m=dec(); starts={s:n for n,(s,_,_) in F.items()}; calls={n:[] for n in F}
 for a in range(BASE,BASE+len(b)-3,2):
  t=m._thumb_bl_target(b,a)
  if t in starts: calls[starts[t]].append(a)
 if calls!=CALLS: raise RuntimeError('direct ingress changed')
 interiors=set()
 for s,e,_ in F.values(): interiors.update(range(s+2,e,2))
 ent=[]; inside=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0]; t=v&~1
  if t in starts: ent.append((BASE+o,v))
  elif t in interiors: inside.append((BASE+o,v))
 if ent!=[(0x4B8784,0x536FA5),(0x536F9C,0x536C5D)] or inside: raise RuntimeError('stored/interior ingress changed')
 from analyze_g2_cordio_l2c_production import validate
 production=validate(source=SOURCE,source_sha256=SOURCE_SHA,
  functions=PRODUCTION_FUNCTIONS,metrics=PRODUCTION_METRICS,
  patch_prefix='replace_cordio_l2c_slave_',region_prefix='cordio_l2c_slave_',
  stock_functions=F,stock_bytes=1078,source_functions=7,
  source_only=['L2cDmSigReq'],region_count=16,hardening={
   'one_based_connection_index_preserved':True,
   'allocation_before_timer_start_hardened':True,
   'response_and_command_reject_lengths_hardened':True,
   'timeout_clears_pending_identifier':True})
 return {'schema_version':1,'module':{'start':0x536B40,'end_exclusive':0x536FBC,'physical_bytes':1148,'linked_function_count':6,'linked_function_bytes':1078,'source_inventory_functions':7,'source_only_functions':['L2cDmSigReq'],'direct_bl_ingress_sites':4,'registered_function_pointers':2,'strict_interior_pointers':0},'architecture':{'dm_conn_max':3,'handle_validation':'DmConnIdByHandle','state_index':'connId-1','retained_source_path':0x6DD594},'lineage':{'selected_blob':'e9a1ff23544bd7e987d53ff7fb6fbfa9b70beef3','selected_sha256':'2f350e0fd27cdc205736df065099da356b9fa8be6e2ce4df014435cde53cbf73','license':'Apache-2.0','historical_generating_commit_resolved':False},'build_readiness':{'status':'production-routed','reason':'host and isolated Cortex-M55 gates green'},'production':production}
def main():
 p=argparse.ArgumentParser();p.add_argument('--image',type=Path,default=IMAGE);p.add_argument('--json',action='store_true');a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else 'Cordio l2c_slave closed: 6 linked, 1 source-only');return 0
if __name__=='__main__': raise SystemExit(main())
