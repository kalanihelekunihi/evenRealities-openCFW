#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for conversate_ui_tag_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-conversate-ui-tag-page-function-map.tsv";CL=ROOT/"tools/manifests/g2-conversate-ui-tag-page-closure.tsv";PM=ROOT/"tools/manifests/g2-conversate-ui-tag-page-provider-map.tsv"
PINS={FM:"dcb646172db38d1c09427b1dd80ad0b4874e6dfa936e215c0fcd374fa8e70b8d",CL:"25c3cb65b1a96bd652ec9514cfe883bf44e5b2cac5a05e17aedbac6edeb73acc",PM:"082bea6cb74c0a20498a85b877bbd5a20a171cf3494e9a5a7ddc5eb08257ed34"}
F=((0x5B5DE4,0x5B5ED2),(0x5B5ED2,0x5B5EF6),(0x5B5EF6,0x5B5F1A),(0x5B5F1A,0x5B5F44),(0x5B5F44,0x5B63D4),(0x5B63D4,0x5B6426),(0x5B6426,0x5B660E),(0x5B660E,0x5B664C),(0x5B664C,0x5B6688),(0x5B6688,0x5B68D6),(0x5B68D6,0x5B6942));PHYS=(0x5B5DE4,0x5B69D4);POOL=(0x5B6942,0x5B69D4)
ENTRIES=[(0x5B1670,0x5B5DE4),(0x5B6530,0x5B63D4),(0x5B6602,0x5B63D4)];STORED=[(0x5B6984,0x5B5F1A),(0x5B69B0,0x5B660E),(0x5B69C8,0x5B664C),(0x686A9C,0x5B6426),(0x686AB4,0x5B5F44),(0x686BEC,0x5B6426),(0x686C0C,0x5B68D6),(0x686C14,0x5B6688),(0x686C34,0x5B5ED2),(0x686C3C,0x5B5EF6),(0x686C94,0x5B6426)]
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439C04,0x43C0E4};CMSIS={0x4490CC}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());lv=json.loads((ROOT/"third_party/lvgl/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or lv["upstream"]["selected_commit"]!="344c7c318047b7348e1be8572a9fd4260c251cfa" or cms["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=11:raise c.AuditError("function inventory changed")
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
 if anch!=1 or len(body)!=2910 or sh(body)!="b9d4e11e0a6251f057f9de20e63cc626127bc4f5828baa857d2b81ab42703fa5" or code!=body or len(ins)!=1087 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="71f6f0dfdab260a310e319fc1bd6b4d5fd87303eaf98d37ae5f49c571abf36dc" or ind:raise c.AuditError("instruction closure changed")
 if sh(c._slice(b,*PHYS))!="dc6fe5f9b76e2877025da3463a30faf87d1c9bcec8f5e62e99bbc55c7e401b8e" or sh(c._slice(b,*POOL))!="b1a650ec73bdd9f4ce38f930b65973f98ccf3a9db8cbd7db89b224aaa4d65369":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x5B5DC0,PHYS[0]))!="d88e1aef4adcd1288bebe3fc1d6264540fe27018bec2606b5b227407ec384e01" or sh(c._slice(b,PHYS[1],0x5B69DC))!="0eb47860ae028557a32878085f4bf39b351cd9695df0ea036dae2dee3005ce42":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts)
 if len(calls)!=204 or sum(y in starts for _,y in calls)!=2 or c._pair_digest(calls)!="4e7557a6cefb6198b4ea5d6bbcc7f3f53d040c195adc910d547ffdbd541e8c42":raise c.AuditError("call topology changed")
 lvgl={x for x in ext if x<0x58C238 and x not in EASY|IAR|CMSIS};first={x for x in ext if x>=0x58C238}
 if (sum(ext[x] for x in EASY),sum(ext[x] for x in IAR),sum(ext[x] for x in CMSIS),len(lvgl),sum(ext[x] for x in lvgl),sum(ext[x] for x in first))!=(40,4,2,50,113,43):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if entries!=ENTRIES or c._pair_digest(entries)!="3d119632ad8865cf0ca8d9db3851889369bfa007587033f4f9fc9f31bf50c06f" or strict:raise c.AuditError("BL entry topology changed")
 stored=[];interior=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];y=v&~1
  if v&1 and y in starts:stored.append((c.BASE+off,y))
  elif v&1 and y in interiors:interior.append((c.BASE+off,y))
 if stored!=STORED or c._pair_digest(stored)!="c05d428d4cbb83168c5b0a46f43c7d0eb9c6f69652c7e5be405fa57bd5dd894c" or interior!=[(0x524C96,0x5B6862)]:raise c.AuditError("stored entry topology changed")
 if t.literal_references(b,0x5B694C)!=[0x5B5D7C,0x5B5E14,0x5B6334,0x5B6484,0x5B64EE,0x5B66F6,0x5B6796,0x5B6830,0x5B68A8]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":11,"body_bytes":2910,"physical_bytes":3056,"outer_pool_bytes":146,"direct_body_calls":204,"internal_direct_body_calls":2,"external_direct_body_calls":202,"direct_bl_entry_sites":3,"stored_entry_pointers":11,"stored_alternate_interior_entries":1,"indirect_body_calls":0},"provider_boundary":{"easylogger_calls":40,"lvgl_calls":113,"cmsis_tick_calls":2,"iar_dlib_calls":4,"first_party_calls":43,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
