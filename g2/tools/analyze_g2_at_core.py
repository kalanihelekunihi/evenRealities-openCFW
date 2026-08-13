#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for eAT at_core.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-at-core-function-map.tsv";CL=ROOT/"tools/manifests/g2-at-core-closure.tsv";PM=ROOT/"tools/manifests/g2-at-core-provider-map.tsv"
PINS={FM:"853b81d8aea60d430d541befc26d9221b5c4c1024ead25919bcab3b8e7ad9809",CL:"484846ed457cf6d8e0c82d2192612816b46af2834a974ec09cf3833ddd4168be",PM:"ade616b5c70094a51481c5230f4f0152099b5960f1881f1aabfcf0d2116a4f9b"};F=((0x5412E0,0x541302),(0x541302,0x54136C),(0x54136C,0x541430),(0x541430,0x5414BA),(0x5414BA,0x54157A));PHYS=(0x5412E0,0x5415B4);POOL=(0x54157A,0x5415B4)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x43C0E4,0x44A43C,0x44B728,0x44B76C,0x4751C8};FIRST={0x57DDFC,0x57DE0A,0x57DEB0};IND=[0x54149A,0x5414B0,0x54147E,0x5414F6]
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
 if anch!=2 or len(body)!=666 or sh(body)!="1a4a9470df59605ee0655a824f38edd00bf481589640c432717967c40c3b4eb5" or code!=body or len(ins)!=281 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="36487bc5e3e7ac0f50fc784fb357310b9affbe9daf33e080e44733c45820bd91":raise c.AuditError("instruction closure changed")
 if ind!=IND or d._address_digest(ind)!="8a05955e46f6fafd5f098d17916b2d3738970a4764256005e6b50445520843e4":raise c.AuditError("indirect call topology changed")
 if sh(c._slice(b,*PHYS))!="ffe5d0bebdc722a192977f973922b2915aa66e0e0c1083ef673acab29a638e0a" or sh(c._slice(b,*POOL))!="d672f0e669a363d991186dfaf619e555ea115bc373776000166151bccfeeeef3":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x5412D8,PHYS[0]))!="5330b09d070eadb9e62b3d1fee341cf881d16d5bc64bd2ff0f75021d808a3787" or sh(c._slice(b,PHYS[1],0x5415C2))!="f95db635787d3076786e44cf1c634d50ae9761506e0eadc2a5a71967c40e67ae":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts)
 if len(calls)!=21 or sum(y in starts for _,y in calls)!=1 or c._pair_digest(calls)!="89dc77834666ef37361d8fa61d982fc93bf6ead8bd47251be48b8d4fd62f9c39" or set(ext)!=EASY|IAR|FIRST:raise c.AuditError("call topology changed")
 if (sum(ext[x] for x in EASY),sum(ext[x] for x in IAR),sum(ext[x] for x in FIRST))!=(10,6,4):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=85 or c._pair_digest(entries)!="2890ada6cbd2be926b11acb7157afccae03f6001498290b4a3119f2711fd5819" or strict:raise c.AuditError("BL entry topology changed")
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];target=v&~1
  if v&1 and (target in starts or target in interiors):raise c.AuditError("unexpected stored entry")
 if t.literal_references(b,0x541594)!=[0x541342,0x5413E0]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[],"public_source_fingerprint_match":False},"surface":{"linked_functions":5,"ghidra_discovered_functions":4,"additional_recovered_functions":1,"path_anchored_functions":2,"body_bytes":666,"physical_bytes":724,"outer_pool_bytes":58,"direct_body_calls":21,"internal_direct_body_calls":1,"external_direct_body_calls":20,"indirect_body_calls":4,"direct_bl_entry_sites":85,"stored_entry_pointers":0},"provider_boundary":{"easylogger_calls":10,"iar_dlib_calls":6,"first_party_parser_calls":4,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
