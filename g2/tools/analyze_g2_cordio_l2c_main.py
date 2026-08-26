#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio L2CAP core unit."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_BYTES=3_523_396;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
PINS={ROOT/'tools/manifests/packetcraft-cordio-l2c-main-function-map.tsv':'08f8f867950d62eeb39e7ae461eae803abc874c460699a28563e8cc2ca94ece9',ROOT/'tools/manifests/packetcraft-cordio-l2c-main-provenance.tsv':'714186c3477775d40ea8bce97db52317b7e3abbf56dceeeb1713526cff5fcbd0'}
SOURCE=ROOT/'components/shared/cordio/runtime_cordio_l2c_main.c'
SOURCE_SHA='0289a81581ac40b849fb642d61fd3f55b51a6e7bda8d343bd750b8cb6f540c24'
PRODUCTION_FUNCTIONS=[
 'open_cfw_cordio_l2c_default_data_callback',
 'open_cfw_cordio_l2c_default_cid_data_callback',
 'open_cfw_cordio_l2c_default_control_callback',
 'open_cfw_cordio_l2c_receive_signaling_packet',
 'open_cfw_cordio_l2c_hci_acl_callback',
 'open_cfw_cordio_l2c_hci_flow_callback',
 'open_cfw_cordio_l2c_send_command_reject',
 'open_cfw_cordio_l2c_message_allocate',
 'open_cfw_cordio_l2c_initialize',
 'open_cfw_cordio_l2c_register',
 'open_cfw_cordio_l2c_data_request',
]
PRODUCTION_METRICS=[
 (353336,2,0),(353340,2,0),(353344,2,0),(353348,70,2),
 (353420,142,2),(353564,88,1),(353652,56,2),(353708,6,1),
 (353716,68,1),(353784,64,0),(353848,52,2),
]
F={'l2cDefaultDataCback':(0x530538,0x530640,'b51fc0704d53534f9e2d60e5085ea34f3286f1212b9ec655f1d211392f68840b'),'l2cDefaultDataCidCback':(0x530640,0x53075E,'1bc7d2db5e7557e18c80e502a490e31b86afa2f0676cd4d78ec2bd4db27fb6c1'),'l2cDefaultCtrlCback':(0x53076C,0x53076E,'c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8'),'l2cRxSignalingPkt':(0x53076E,0x5308E6,'c26ae1510d3d56ca5de518313cd89389c877a3f1047c4512ab0a547e05db9f7d'),'l2cHciAclCback':(0x5308E6,0x530A9C,'11f76d172ff57564eb7a1581fd078cf32ca57644e4dd2980ba9c29bd19717a39'),'l2cHciFlowCback':(0x530AA4,0x530ADC,'2f76d36b8b21279faa6824e021362b37d6f5728ba9503a34fa91e5dc1fa51d17'),'l2cSendCmdReject':(0x530AE0,0x530B28,'967b8eb767f2ba09f61aa75f06f713e2ad5377dd07d6a21a01e6e4c9a1eb1b10'),'l2cMsgAlloc':(0x530B28,0x530B34,'bf3a39fbd761825cc61f5b64a83c139bed38809221d70a03a0d1d148863219e5'),'L2cInit':(0x530B34,0x530B5E,'cb21c7a5d22c959e24d20e4242a34160cec9fb326fbd6320d9efb36f0aba4bff'),'L2cRegister':(0x530B5E,0x530B74,'395e5ffd4e439b64aa157aefc59e91cad11a2529c8ba54fd6f83a87983b9c86a'),'L2cDataReq':(0x530BBC,0x530BFE,'60f3c18cb48c5b48e80d8596f2c6332e03168223a46bed16a4073e08e825ee09')}
CALLS={'l2cDefaultDataCback':[],'l2cDefaultDataCidCback':[],'l2cDefaultCtrlCback':[],'l2cRxSignalingPkt':[],'l2cHciAclCback':[],'l2cHciFlowCback':[],'l2cSendCmdReject':[0x536E6E,0x537144],'l2cMsgAlloc':[0x530AEA,0x536ED2,0x53723A],'L2cInit':[0x4B8048],'L2cRegister':[0x4B5138,0x537CEA],'L2cDataReq':[0x4B50CA,0x4B561C,0x4B5986,0x530B22,0x534E9E,0x536F64,0x537272,0x537BB2]}
STORED=[(0x530BA4,0x530539),(0x530BA8,0x53076F),(0x530BAC,0x53076D),(0x530BB0,0x530641),(0x530BB4,0x530AA5),(0x530BB8,0x5308E7)]
GAPS=[(0x53075E,0x53076C,'6e21e0438a5b4117358cc394ac7bf45b830b0e5a77a8ebbb971b6b03432f32a8'),(0x530A9C,0x530AA4,'501c2d42ed0da2384e005b2f302d3d72aa0bf9f01f3526b289125f2494ec285f'),(0x530ADC,0x530AE0,'dc81150db97a1851e655b42e04fc71865b2f3d1a70ff32ff48962214db47fe1a'),(0x530B74,0x530BBC,'4c9039eaf69f8c49eab37a23040f71953e89f838406bce607c9b7079baddfd10'),(0x530BFE,0x530C00,'96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7')]
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,s,e):return b[s-BASE:e-BASE]
def dec():
 sys.path.insert(0,str(ROOT/'tools'));p=ROOT/'tools/recover_apollo_embedded_source_paths.py';q=importlib.util.spec_from_file_location('l2c_main_thumb',p);m=importlib.util.module_from_spec(q);sys.modules[q.name]=m;q.loader.exec_module(m);return m
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
 if sha(b''.join(bodies))!='c64494e81c1cb07880a0fd3905c7c9c6e702da69a534a8714ddeab0831c08312':raise RuntimeError('body concat changed')
 if sha(sl(b,0x530538,0x530C00))!='561273571edcc15932fba3b4f5b4f5c3fc766a8a60ae933885a7173d02f8ccd9':raise RuntimeError('physical object changed')
 for s,e,h in GAPS:
  if sha(sl(b,s,e))!=h:raise RuntimeError(f'inline data changed at {s:#x}')
 pool=sl(b,0x530B74,0x530BBC)
 words=list(struct.unpack('<18I',pool))
 if words[3]!=0x006DD4D4 or words[7]!=0x200737D8 or words[12:]!=[v for _,v in STORED]:raise RuntimeError('literal/callback pool changed')
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
 if ent!=STORED or inside:raise RuntimeError('stored/interior ingress changed')
 from analyze_g2_cordio_l2c_production import validate
 production=validate(source=SOURCE,source_sha256=SOURCE_SHA,
  functions=PRODUCTION_FUNCTIONS,metrics=PRODUCTION_METRICS,
  patch_prefix='replace_cordio_l2c_main_',region_prefix='cordio_l2c_main_',
  stock_functions=F,stock_bytes=1636,source_functions=11,source_only=[],
  region_count=28,copy_indexes={3},hardening={
   'acl_and_signaling_length_bounds_hardened':True,
   'connection_and_role_bounds_hardened':True,
   'null_callback_and_registration_bounds_hardened':True})
 return {'schema_version':1,'module':{'start':0x530538,'end_exclusive':0x530C00,'physical_bytes':1736,'linked_function_count':11,'linked_function_bytes':1636,'source_inventory_functions':11,'source_only_functions':[],'direct_bl_ingress_sites':16,'registered_function_pointers':6,'strict_interior_pointers':0},'architecture':{'source_bodies_release_invariant':True,'retained_source_path':0x006DD4D4,'control_block':0x200737D8,'identifier_initial_value':1,'hci_callbacks_registered':True,'neighboring_dm_abi':'r20/R4'},'lineage':{'selected_blob':'988b73a635704e49059871a2e2e59a59166b29c4','selected_sha256':'b76edc13a463028e60c6b148d90c47bc9dbb8f2a8783ac8efc1f765fc722d951','license':'Apache-2.0','independent_release_discriminator':False},'build_readiness':{'status':'production-routed','reason':'host and isolated Cortex-M55 gates green'},'production':production}
def main():
 p=argparse.ArgumentParser();p.add_argument('--image',type=Path,default=IMAGE);p.add_argument('--json',action='store_true');a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else 'Cordio l2c_main closed: 11 linked');return 0
if __name__=='__main__':raise SystemExit(main())
