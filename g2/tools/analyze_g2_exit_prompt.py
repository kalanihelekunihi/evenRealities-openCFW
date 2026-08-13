#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for exit_prompt.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-exit-prompt-function-map.tsv";CL=ROOT/"tools/manifests/g2-exit-prompt-closure.tsv";PM=ROOT/"tools/manifests/g2-exit-prompt-provider-map.tsv"
PINS={FM:"dbbd08e7a4b950f65559acc4ddb9c052626f63c13b5a85ac445aad5c67f71408",CL:"1ed84fd47dd01f508b117b7195e2f9fa04910b5d66bb344f52bab597345d417e",PM:"7903d830ef1ada729cf40526f3c5a567288d59fbf2915c3a49e41df60d1c940c"}
F=((0x58BDA8,0x58BE1A),(0x58BE1A,0x58BEBC),(0x58BEBC,0x58BF12),(0x58BF12,0x58BFB2),(0x58BFB2,0x58C0B6));PHYS=(0x58BDA8,0x58C12C);POOL=(0x58C0B6,0x58C12C)
ENTRIES=[(0x5557F0,0x58BFB2),(0x556BCE,0x58BFB2),(0x556BF6,0x58BFB2),(0x556C2C,0x58BFB2),(0x58BE5C,0x58BDA8),(0x58C090,0x58BDA8),(0x58C0AA,0x58BF12),(0x59E146,0x58BFB2),(0x59E16E,0x58BFB2),(0x59E1A0,0x58BFB2),(0x59E1C8,0x58BFB2),(0x59E428,0x58BFB2),(0x5B19DC,0x58BFB2),(0x5B1A02,0x58BFB2),(0x5B1A38,0x58BFB2),(0x5B1A5C,0x58BFB2),(0x5B5958,0x58BFB2)]
STORED=[(0x58C0FC,0x58BE1A),(0x58C110,0x58BEBC),(0x58C128,0x58BF12)]
EASY={0x43CE9E,0x43D0CE,0x43D574};LVGL={0x43F4C0,0x43F6B8,0x44104C,0x44140E,0x44143E,0x44145A,0x443504,0x44D878,0x450500,0x45A568,0x464C36,0x499416,0x49942E};FIRST={0x58C238,0x58C426,0x58C516}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());lv=json.loads((ROOT/"third_party/lvgl/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or lv["upstream"]["selected_commit"]!="344c7c318047b7348e1be8572a9fd4260c251cfa":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=5:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0)
  if (a,z)!=bounds:raise c.AuditError("bounds changed")
  raw=c._slice(b,a,z)
  if len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=2 or len(body)!=782 or sh(body)!="940912d6dc546e8c0e6eecdf4dc735f0251eb026bbdc5b54713afe3ab0024639" or code!=body or len(ins)!=314 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="719c0e1203215564f8e46731a1a8707348aa7bb9ee1d07af2221acc6cc7f8ed5" or ind:raise c.AuditError("instruction closure changed")
 if sh(c._slice(b,*PHYS))!="2f325979bf7ed9bfcc82823ed8b0708365b655bf0fc265c21c59903cbe0c3a37" or sh(c._slice(b,*POOL))!="67644555460217c7f931a705c268d4fd412417124bcb1b3827c7c062d5a11ae7":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x58BD86,PHYS[0]))!="e70876af70a42d8e2a58fd55ce310ed2e9566c94069228293752635a90bc9bbe" or sh(c._slice(b,PHYS[1],0x58C138))!="0bd2e16e12873a9d329411d10042b2bff7f9d41da848b0eec03f76f5abeb8948":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts)
 if len(calls)!=56 or sum(y in starts for _,y in calls)!=3 or c._pair_digest(calls)!="ffa20f597252b6a0bd6636d3cfa464ca137d6fdb98bc368cbec8361aa144e4d5" or set(ext)!=EASY|LVGL|FIRST:raise c.AuditError("call topology changed")
 if (sum(ext[x] for x in EASY),sum(ext[x] for x in LVGL),sum(ext[x] for x in FIRST))!=(35,15,3):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if entries!=ENTRIES or c._pair_digest(entries)!="03e6848326e52f74588336e43cf15b65a1742ae8d29e52ed29ba77eedb4332bd" or strict:raise c.AuditError("BL entry topology changed")
 stored=[];strict=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];y=v&~1
  if v&1 and y in starts:stored.append((c.BASE+off,y))
  elif v&1 and y in interiors:strict.append((c.BASE+off,y))
 if stored!=STORED or c._pair_digest(stored)!="8a726a514441575b270fb0b5688bbdea9e98c5bbb9d4db730e801ebbf1dfd506" or strict:raise c.AuditError("stored entry topology changed")
 if t.literal_references(b,0x58C0C0)!=[0x58BDE0,0x58BE2E,0x58BE94,0x58BED6,0x58BF26,0x58BFD6,0x58C02A]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":5,"ghidra_discovered_functions":2,"additional_recovered_functions":3,"path_anchored_functions":2,"body_bytes":782,"physical_bytes":900,"outer_pool_bytes":118,"direct_body_calls":56,"internal_direct_body_calls":3,"external_direct_body_calls":53,"direct_bl_entry_sites":17,"stored_entry_pointers":3,"indirect_body_calls":0},"provider_boundary":{"easylogger_calls":35,"lvgl_calls":15,"first_party_calls":3,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
