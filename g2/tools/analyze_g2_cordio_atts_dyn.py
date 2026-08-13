#!/usr/bin/env python3
"""Fail-closed exclusion audit for optional dynamic ATT services on G2."""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_BYTES=3_523_396;IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
FM=ROOT/'tools/manifests/packetcraft-cordio-atts-dyn-function-map.tsv';PV=ROOT/'tools/manifests/packetcraft-cordio-atts-dyn-provenance.tsv'
PINS={FM:'b21727d6506291c5ee83faced8b7758d24f82107a3accf1d934d1cb3bfe3e902',PV:'28e7da04ff9e4d6d0c8cc9f557e5cb242eec02a381a2440a9eb814545100eb15'}
ATTS_ADD_GROUP=0x5353AE;ADD_CALLERS=[0x52DC10,0x52DC16,0x5361A8,0x5361C0,0x5361D8,0x5361F0,0x536208,0x536220]
ATTS_REMOVE_GROUP=0x5353E8;REMOVE_CALLERS=[0x534DB8]
ABSENT=(b'atts_dyn.c',b'AttsDynInit',b'AttsDynCreateGroup',b'AttsDynAddAttr',b'attsDynHeap',b'hidapp_main.c')
def sha(x):return hashlib.sha256(x).hexdigest()
def dec():
 sys.path.insert(0,str(ROOT/'tools'));p=ROOT/'tools/recover_apollo_embedded_source_paths.py';q=importlib.util.spec_from_file_location('atts_dyn_thumb',p);m=importlib.util.module_from_spec(q);sys.modules[q.name]=m;q.loader.exec_module(m);return m
def analyze(image_path=IMAGE):
 b=image_path.read_bytes()
 if len(b)!=IMAGE_BYTES or sha(b)!=IMAGE_SHA:raise RuntimeError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise RuntimeError(f'pinned input changed: {p}')
 with FM.open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
 if len(rows)!=7 or any(r['stock_status']!='dead_stripped' or r['stock_address']!='-' for r in rows):raise RuntimeError('source inventory changed')
 for marker in ABSENT:
  if marker in b:raise RuntimeError(f'unexpected dynamic-ATT marker appeared: {marker!r}')
 m=dec();calls={ATTS_ADD_GROUP:[],ATTS_REMOVE_GROUP:[]}
 for a in range(BASE,BASE+len(b)-3,2):
  t=m._thumb_bl_target(b,a)
  if t in calls:calls[t].append(a)
 if calls[ATTS_ADD_GROUP]!=ADD_CALLERS or calls[ATTS_REMOVE_GROUP]!=REMOVE_CALLERS:raise RuntimeError('group API caller closure changed')
 return {'schema_version':1,'module':{'classification':'not_linked_or_dead_stripped','linked_function_count':0,'linked_function_bytes':0,'source_inventory_functions':7,'source_only_functions':[r['function'] for r in rows],'retained_path_anchors':0,'semantic_body_anchors':0},'exclusion':{'atts_add_group_callers':ADD_CALLERS,'atts_remove_group_callers':REMOVE_CALLERS,'dynamic_group_provider_callers':0,'dynamic_heap_bytes_not_instantiated':1280,'retained_dynamic_markers':0,'official_consumer_topology':'only HID/battery dynamic service builders; every builder reaches AttsAddGroup through AttsDynAddAttr or AttsDynAddAttrConst'},'lineage':{'selected_optional_blob':'a125a644317eb973674637ea6fa0391c13999bf2','selected_optional_sha256':'fb310af2be69489884b104a35288f3539c2bb47dbc6ebe48d4070e3133cea9d3','license':'Apache-2.0','stock_body_version_discriminated':False,'implementation_release_invariant':True},'production':{'stock_bytes_replaced':0,'source_owned_bytes_added':0}}
def main():
 p=argparse.ArgumentParser();p.add_argument('--image',type=Path,default=IMAGE);p.add_argument('--json',action='store_true');a=p.parse_args();r=analyze(a.image);print(json.dumps(r,indent=2,sort_keys=True) if a.json else 'Cordio atts_dyn excluded: 7 source-only');return 0
if __name__=='__main__':raise SystemExit(main())
