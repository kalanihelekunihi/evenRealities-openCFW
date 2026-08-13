#!/usr/bin/env python3
"""Validate the hidden temperature consumer, cache, and redacting daily callbacks."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256

RANGES = {
 (0x5BE5C,0x5BE60):"06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
 (0x5BE64,0x5BE78):"ddffa6a9d531bb13b398e2be366b7d24f03b26a81e6a459f0c1d3edd13342abb",
 (0x5BE7C,0x5BF74):"7b8db4e9a6bf5ad8d8391f5ba9d1138e222a8a1cedb81ba754282e9dee68c489",
 (0x8A8FC,0x8A928):"9b7722026f3f79e3ddfc03fab438f004fd4b51f1aa0cc9a4ba272914ff2f4cf7",
 (0x918DE,0x918F8):"47bc9c4de0976d85ef7124264b097822457ea760c8834498fab08e28a949e18d",
 (0x91918,0x91950):"79962b493ae679648063ea25a844f774629cca4f0042d72575ed38307c7de6b4",
 (0x91954,0x9196E):"6bdfc2d55b366385c677e0f1d6228b61d9d9adf9cf1c9c2aefbd9229304bffe6",
}
BRANCHES = {
 0x5BE5C:[0x8B222,0x8B5C0,0x8E562,0x918E4,0x9191E,0x9195A],
 0x5BE64:[0x8E69C], 0x5BE7C:[0x8A922], 0x8A8FC:[0x42A18],
}
LITERALS={0x5BE60:0x200165F4,0x5BE78:0x200165F4,0x5BF74:0x200165F4,0x91950:0x38640900}
DESCRIPTOR=0x99C14
EXPECTED=bytes.fromhex("020300001919090055190900df180900")

def fb(image,base,start,end):
 o=mapped_offset(start,base,len(image)); return image[o:o+end-start]

def summarize(path,base):
 image=path.read_bytes(); digest=hashlib.sha256(image).hexdigest()
 if digest!=IMAGE_SHA256: raise ValueError(f"unexpected image SHA-256: {digest}")
 ranges=[]
 for (s,e),wanted in RANGES.items():
  got=hashlib.sha256(fb(image,base,s,e)).hexdigest()
  if got!=wanted: raise ValueError(f"range {s:x}...{e:x}: {got}")
  ranges.append({"start":f"0x{s:08x}","end_exclusive":f"0x{e:08x}","sha256":got})
 branches={}
 for target,wanted in BRANCHES.items():
  got=[a for a,_ in direct_thumb_branches_to(image,base,target)]
  if got!=wanted: raise ValueError(f"branches to {target:x}: {got}")
  branches[f"0x{target:08x}"]=[f"0x{x:08x}" for x in got]
 literals={}
 for a,wanted in LITERALS.items():
  got=struct.unpack("<I",fb(image,base,a,a+4))[0]
  if got!=wanted: raise ValueError(f"literal {a:x}: {got:x}")
  literals[f"0x{a:08x}"]=f"0x{got:08x}"
 descriptor=fb(image,base,DESCRIPTOR,DESCRIPTOR+16)
 if descriptor!=EXPECTED: raise ValueError(descriptor.hex())
 return {"image":str(path),"image_sha256":digest,"load_base":f"0x{base:08x}",
  "verified_ranges":ranges,"direct_branches":branches,"literals":literals,
  "descriptor":{"address":f"0x{DESCRIPTOR:08x}","raw_hex":descriptor.hex(),"metric_index":2,
   "slot_bytes":3,"callbacks_thumb":[f"0x{struct.unpack_from('<I',descriptor,o)[0]:08x}" for o in (4,8,12)]},
  "consumer":{"accepted_published_range":[250,500],"timestamp_always_replaced":True,
   "stored_offset":"published_minus_250","storage_notification":None},
  "cache":{"address":"0x200165f4","bytes":84,"rolling_accumulator":"0x20016658",
   "two_independent_hour_calls":True,"latest_accessor":None},
  "daily":{"stock_index_bounds":False,"cutoff":946080000,"invalid_early_nonzero_redacted":True,
   "clock_reads":1,"offline_queue":None,"history_phone_route":False},
  "safety":{"executes_firmware":False,"physical_device_access":False,"ble_access":False,
   "sensor_access":False,"flash_writes":False,"health_store_access":False}}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("image",type=Path)
 p.add_argument("--base",type=lambda x:int(x,0),default=DEFAULT_BASE);a=p.parse_args()
 print(json.dumps(summarize(a.image,a.base),indent=2,sort_keys=True))
if __name__=="__main__": main()
