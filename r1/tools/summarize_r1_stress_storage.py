#!/usr/bin/env python3
"""Validate the dormant stress consumer/cache, HRV alias, and plain daily callbacks."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256

RANGES = {
 (0x5BCCC,0x5BCD0):"06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
 (0x5BCD4,0x5BCE8):"f3ca3c0277320be3a8cb0a53e34e75942aea91cea3cba9986cf7f5a81e1fa33c",
 (0x5BCEC,0x5BDC8):"5141c95e2effacf13e132c8bbf97e7ee2b1ddcde8226adc379acbf803724ea41",
 (0x8A8D8,0x8A8FC):"69f01f7386e5f6635632ee06563299c88f95c46ffe7027f954345bfdc9c72567",
 (0x91124,0x9113E):"6a2af6247e7a7644a10749e1bfa9f9e2c5b73c4b56e6ce1f82ecfeffbf491987",
 (0x9113E,0x91158):"be1a5a382df0d73d346bba550551db03de167a560f1c2e358bf51a4c36385967",
 (0x91158,0x91172):"30000ecadfe2a7b1ffd38113c40dda4f3ffdae43c5f1f020642368553d8d9842",
}
BRANCHES={
 0x5BCCC:[0x8B23E,0x9112A,0x91144,0x9115E],
 0x5BCD4:[0x8E558],0x5BCEC:[0x8A8F6],0x8A8D8:[0x429C4],
}
LITERALS={0x5BCD0:0x20016670,0x5BCE8:0x20016670,0x5BDC8:0x20016670}
DESCRIPTOR=0x99C24
EXPECTED=bytes.fromhex("030300003f1109005911090025110900")

def fb(image,base,start,end):
 o=mapped_offset(start,base,len(image)); return image[o:o+end-start]

def summarize(path,base):
 image=path.read_bytes();digest=hashlib.sha256(image).hexdigest()
 if digest!=IMAGE_SHA256: raise ValueError(digest)
 ranges=[]
 for (s,e),wanted in RANGES.items():
  got=hashlib.sha256(fb(image,base,s,e)).hexdigest()
  if got!=wanted: raise ValueError(f"range {s:x}...{e:x}: {got}")
  ranges.append({"start":f"0x{s:08x}","end_exclusive":f"0x{e:08x}","sha256":got})
 branches={}
 for target,wanted in BRANCHES.items():
  got=[a for a,_ in direct_thumb_branches_to(image,base,target)]
  if got!=wanted: raise ValueError(f"branches {target:x}: {got}")
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
  "descriptor":{"address":f"0x{DESCRIPTOR:08x}","raw_hex":descriptor.hex(),"metric_index":3,
   "slot_bytes":3,"callbacks_thumb":[f"0x{struct.unpack_from('<I',descriptor,o)[0]:08x}" for o in (4,8,12)]},
  "consumer":{"accepted_range":[0,100],"timestamp_always_replaced":True,
   "storage_notification":None,"phone_history_route":False},
  "cache":{"address":"0x20016670","bytes":84,"rolling_accumulator":"0x20016660",
   "two_independent_hour_calls":True,"latest_accessor":None,
   "aliases_hrv_accumulator_address":"0x20016670"},
  "daily":{"stock_index_bounds":False,"clock_reads":0,"redaction":False,
   "offline_queue":None,"acknowledgement":None},
  "safety":{"executes_firmware":False,"physical_device_access":False,"ble_access":False,
   "sensor_access":False,"flash_writes":False,"health_store_access":False}}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("image",type=Path)
 p.add_argument("--base",type=lambda x:int(x,0),default=DEFAULT_BASE);a=p.parse_args()
 print(json.dumps(summarize(a.image,a.base),indent=2,sort_keys=True))
if __name__=="__main__":main()
