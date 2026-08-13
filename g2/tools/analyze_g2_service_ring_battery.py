#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for service_ring_battery.c."""
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-service-ring-battery-function-map.tsv";CL=ROOT/"tools/manifests/g2-service-ring-battery-closure.tsv";PM=ROOT/"tools/manifests/g2-service-ring-battery-provider-map.tsv"
PINS={FM:"1c3e5ed36c1382bc3adc62683ee8a26887f702a11c8b0be5fbfadbd0dce06bc0",CL:"105bb36b1c85bb6c73a732b04eaee6ee6a8765ca260a1a799eda55d03db66b7e",PM:"b9544563bc91ead78b1d39b6abd218b7cabf5880c8d09844249d2a24f1e7e4f1"}
F=((0x4FF8E4,0x4FF96C),(0x4FF96C,0x4FF98A),(0x4FF98A,0x4FF994),(0x4FF994,0x4FF99A),(0x4FF99A,0x4FFA44));PHYS=(0x4FF8E4,0x4FFA70);POOL=(0x4FFA44,0x4FFA70)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4};TRANSPORT={0x464D1C,0x4651E0}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=5:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=2 or len(body)!=352 or sh(body)!="77f223b6c8cf312ccbbccb79e41c1b54fedc36cb3c2204902ba346d646485377" or code!=body or len(ins)!=146 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="c634c54f4c510b068d1a98005d65162f483c7d8de17b91fe1ea6f0f1f0598287" or ind:raise c.AuditError("instruction closure changed")
 if sh(c._slice(b,*PHYS))!="671ac6562c8d006acb17e39d816e19a2cd6c00887edac1cbeebb0364a36c459e" or sh(c._slice(b,*POOL))!="5b6f8497a0d814000f0d5eaea1d73ffb2ebb5244884a04b357514cbec88b30cd":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x4FF7DC,PHYS[0]))!="f04b9f03dcdcb9940020eea098e1be9a8736eafbb4c2bc9f0d5055d020d49eb3" or sh(c._slice(b,PHYS[1],0x4FFAC8))!="c17ac5e6e1670deebd0fa2388b5c777a837692ede5eccb76a20319bc8e8becb9":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,IAR,TRANSPORT)
 if len(calls)!=19 or sum(y in starts for _,y in calls)!=0 or c._pair_digest(calls)!="ab0009c7054662dc96cfe2e1966057a9e7e1dccf1bca45a9706544adc63f176f" or set(ext)!=set().union(*providers):raise c.AuditError("call topology changed")
 if tuple(sum(ext[x] for x in group) for group in providers)!=(15,2,2):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=9 or c._pair_digest(entries)!="e9d3a2205c922d079f8480f12d9fcfe482ea37b4eb69ed02e580a1ecbb94bab9" or strict:raise c.AuditError("BL entry topology changed")
 if t.literal_references(b,0x4FFA4C)!=[0x4FF940,0x4FF9DE,0x4FFA1A]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":5,"ghidra_discovered_functions":5,"path_anchored_functions":2,"body_bytes":352,"physical_bytes":396,"outer_pool_bytes":44,"direct_body_calls":19,"internal_direct_body_calls":0,"external_direct_body_calls":19,"indirect_body_calls":0,"direct_bl_entry_sites":9,"stored_entry_pointers":0},"provider_boundary":{"easylogger_calls":15,"iar_dlib_calls":2,"first_party_transport_calls":2,"easylogger_commit":"a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
