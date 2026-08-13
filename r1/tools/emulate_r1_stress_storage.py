#!/usr/bin/env python3
"""Execute dormant production stress storage and daily callbacks in private RAM."""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path
from typing import Any
import emulate_r1_spo2_storage as common

common.CONSUMER=0x0008A8D8
common.RESET=0x00091124
common.READ=0x0009113E
common.WRITE=0x00091158
common.CACHE=0x20016670
common.ACCUMULATOR=0x20016660

class StressFixture(common.SpO2Fixture):
 def event(self,value:int,timestamp:int,*,aggregate_hour:int,average_hour:int)->dict[str,Any]:
  self.timestamp_returns=[timestamp];self.local_hour_returns=[aggregate_hour,average_hour]
  pt=self.timestamp_calls;ph=self.local_hour_calls
  self.machine.uc.mem_write(common.EVENT,bytes([value,1,2,3,4,5,6,7]))
  self.machine.call(common.CONSUMER,common.EVENT)
  cache=bytes(self.machine.uc.mem_read(common.CACHE,common.CACHE_LENGTH))
  acc=bytes(self.machine.uc.mem_read(common.ACCUMULATOR,8))
  return {"value":value,"event_after_hex":bytes(self.machine.uc.mem_read(common.EVENT,8)).hex(),
   "timestamp_calls":self.timestamp_calls-pt,"local_hour_calls":self.local_hour_calls-ph,
   "slot":common.aggregate(cache,aggregate_hour*3),
   "accumulator":dict(zip(("hour","reserved","count","sum"),struct.unpack("<BBHI",acc))),
   "latest_point_hex":cache[0x4b:0x50].hex(),
   "notification":self.notifications[-1] if self.notifications else None}
 def read_plain(self,index:int)->dict[str,Any]:
  pt=self.timestamp_calls
  self.machine.uc.mem_write(common.SLOT_OUTPUT,b"\x5a"*3)
  self.machine.call(common.READ,index,common.SLOT_OUTPUT)
  return {"output":common.aggregate(bytes(self.machine.uc.mem_read(common.SLOT_OUTPUT,3))),
   "timestamp_calls":self.timestamp_calls-pt}

def run(image:bytes)->dict[str,Any]:
 ordinary=StressFixture(image).event(50,0x12345678,aggregate_hour=4,average_hour=5)
 minimum=StressFixture(image).event(0,9,aggregate_hour=6,average_hour=6)
 maximum=StressFixture(image).event(100,10,aggregate_hour=7,average_hour=7)
 rejected=StressFixture(image).event(101,11,aggregate_hour=1,average_hour=1)
 reset_fixture=StressFixture(image);reset_fixture.machine.uc.mem_write(common.CACHE,b"\xa5"*0x54)
 rr=reset_fixture.reset(0x01020304,-300)
 reset={"slots_zero":rr[:0x48]==b"\0"*0x48,"utc_offset_minutes":struct.unpack_from("<h",rr,0x48)[0],
  "preserved_4a_4f_hex":rr[0x4a:0x50].hex(),"day_start":struct.unpack_from("<I",rr,0x50)[0]}
 daily=StressFixture(image);daily.reset(0,0);daily.write(5,(50,80,20));plain=daily.read_plain(5)
 assert ordinary["event_after_hex"]=="3201020378563412"
 assert ordinary["timestamp_calls"]==1 and ordinary["local_hour_calls"]==2
 assert ordinary["slot"]=={"average":50,"maximum":50,"minimum":50}
 assert ordinary["accumulator"]=={"hour":5,"reserved":0,"count":1,"sum":50}
 assert ordinary["latest_point_hex"]=="3278563412" and ordinary["notification"] is None
 assert minimum["slot"]=={"average":0,"maximum":0,"minimum":0}
 assert maximum["slot"]=={"average":100,"maximum":100,"minimum":100}
 assert rejected["timestamp_calls"]==0 and rejected["local_hour_calls"]==0
 assert reset=={"slots_zero":True,"utc_offset_minutes":-300,
  "preserved_4a_4f_hex":"a5"*6,"day_start":0x01020304}
 assert plain=={"output":{"average":50,"maximum":80,"minimum":20},"timestamp_calls":0}
 return {"storage_accepted_50":ordinary,"storage_accepted_minimum_0":minimum,
  "storage_accepted_maximum_100":maximum,"storage_rejected_above_100":rejected,
  "reset":reset,"daily_read_is_plain_copy":plain,
  "hrv_alias":{"stress_cache":"0x20016670","hrv_accumulator":"0x20016670"},
  "safety":{"physical_device_access":False,"ble_access":False,"sensor_access":False,
   "flash_writes":False,"health_store_access":False}}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("image",type=Path);a=p.parse_args()
 print(json.dumps(run(a.image.read_bytes()),indent=2,sort_keys=True))
if __name__=="__main__":main()
