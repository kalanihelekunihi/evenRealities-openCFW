#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for thread_notification.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-thread-notification-function-map.tsv";CL=ROOT/"tools/manifests/g2-thread-notification-closure.tsv";PM=ROOT/"tools/manifests/g2-thread-notification-provider-map.tsv"
PINS={FM:"0a722fc216f349a5dce692b627062e730d6fee36c73149fbab11d99d7d0a3b11",CL:"f18a972042ba6897dee3fecf0efd2d2eca8a754f2536af4c8e920ec913b625b4",PM:"881504b0abda7a5cf6bf9070aaeb88ea9c6f174fdca6c5b9954e8174f2294aef"}
F=((0x48E154,0x48E1CC),(0x48E1CC,0x48E1CE),(0x48E1CE,0x48E1F6),(0x48E1F6,0x48E1FE),(0x48E1FE,0x48E208),(0x48E208,0x48E212),(0x48E212,0x48E242),(0x48E25E,0x48E2B8),(0x48E2B8,0x48E34E),(0x48E34E,0x48E3E2),(0x48E3E2,0x48E42E));PHYS=(0x48E154,0x48E484);POOLS=((0x48E242,0x48E25E),(0x48E42E,0x48E484))
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490E2,0x449238,0x4492C2,0x449376,0x449A32,0x449B3C,0x449BEC};FIRST={0x474D16,0x4972C2,0x497960,0x4C9B86,0x4C9BE2,0x4C9C3C,0x4D6A5C,0x4D6BA8,0x5FA0A4};STORED=[(0x48E44C,0x48E154),(0x794117,0x48E212)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cms["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=11:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=3 or len(body)!=702 or sh(body)!="80854793c072c0b9e76acab5f59d55acd08f0c63fe5e27bb3e66b50bed6fff52" or code!=body or len(ins)!=271 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="2f1e5a7fff0098e51d05cbd646541f09fb7285d45a86564921832b15056b6431" or ind:raise c.AuditError("instruction closure changed")
 pool=b"".join(c._slice(b,*bounds) for bounds in POOLS)
 if sh(c._slice(b,*PHYS))!="24b82e6135ae9148a9ae3c4ddfb62fd5dbfc56d1f8614b1b985efee790a767b9" or len(pool)!=114 or sh(pool)!="69df14f4a6473c68592cb4be0461aa5d57e7fd5324fa9caec6c4952cabec843f":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x48E0A8,PHYS[0]))!="3364aa7bd737a4436eee41df6a102a6c60a774ceb30350e2e2d29dda5fd9df2b" or sh(c._slice(b,PHYS[1],0x48E494))!="f27e504dc20d0f5c8f1e8e78135ae9082765054660b5ac65e7994f50caab1df9":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,FIRST)
 if len(calls)!=56 or sum(y in starts for _,y in calls)!=8 or c._pair_digest(calls)!="729bac9a5e50d8b538325b3fbe8bf19b213a0ae78603470e7f0d221d9ed8c975" or set(ext)!=set().union(*providers):raise c.AuditError("call topology changed")
 if tuple(sum(ext[x] for x in group) for group in providers)!=(30,7,11):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=9 or c._pair_digest(entries)!="e5602bc285f8c623c1909b60323cc16ea467bd6af9e314ed347f8feece4c2ed0" or strict:raise c.AuditError("BL entry topology changed")
 stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];target=v&~1
  if v&1 and target in starts:stored.append((c.BASE+off,target))
 if stored!=STORED or c._pair_digest(stored)!="81c35ccb0bf7d083c22334292af3dbcd7abe1d3743fa766a0356425d3aa5a556":raise c.AuditError("stored entry topology changed")
 if t.literal_references(b,0x48E438)!=[0x48E19E,0x48E2D4,0x48E31A,0x48E37A,0x48E3B2,0x48E3FA]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":11,"ghidra_discovered_functions":9,"restored_functions":2,"path_anchored_functions":3,"body_bytes":702,"physical_bytes":816,"outer_pool_bytes":114,"direct_body_calls":56,"internal_direct_body_calls":8,"external_direct_body_calls":48,"indirect_body_calls":0,"direct_bl_entry_sites":9,"stored_entry_pointers":2},"provider_boundary":{"easylogger_calls":30,"cmsis_freertos_calls":7,"first_party_calls":11,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","cmsis_wrappers":["osThreadNew","osThreadFlagsSet","osThreadFlagsWait","osDelay","osMessageQueueNew","osMessageQueueGet","osMessageQueueDelete"],"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
