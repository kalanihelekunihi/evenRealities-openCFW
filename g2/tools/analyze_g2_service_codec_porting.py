#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for service_codec_porting.c."""
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-service-codec-porting-function-map.tsv";CL=ROOT/"tools/manifests/g2-service-codec-porting-closure.tsv";PM=ROOT/"tools/manifests/g2-service-codec-porting-provider-map.tsv"
PINS={FM:"337862aacdaa492a409533d35cd3e0febbacd71efa315dfb79bbbe224adeff63",CL:"8a5e169787e75529e3b41ac3b40f52d32b97f09bc2a882d5213cc609311372f6",PM:"d5d00d196ab80981a3ce83c25e59ef3f7d59d46d82cb5d89356a84f6f5677081"}
F=((0x58FB52,0x58FC0C),(0x58FC0C,0x58FCA8));PHYS=(0x58FB52,0x58FCF0);POOL=(0x58FCA8,0x58FCF0);EASY={0x43CE9E,0x43D0CE,0x43D574};RING={0x598160};UART={0x55E5BC,0x55E630,0x55E8F0}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());ring=json.loads((ROOT/"third_party/ring-buffer/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or ring["upstream"]["selected_commit"]!="190e30bebcec22d7311fd941179d70b4f439c441" or ring["selection"]["compatible_floor_commit"]!="cda00e1efb815bad5100757f0d10d117f633ced6":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=2:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=2 or len(body)!=342 or sh(body)!="7f6f4ef925199c29fde103206f6df39a4c02eb627765b2a3a856be3886847208" or code!=body or len(ins)!=141 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="ce83b160ac6abc49117a7b04d9bfe1af85435ff32546e86142f691f068265bca" or ind:raise c.AuditError("instruction closure changed")
 if sh(c._slice(b,*PHYS))!="10446a3c12344e7c02b1db8fe77c8d28435274bab0f5b6158c641db553b71ef8" or sh(c._slice(b,*POOL))!="96a643a249fff315b45a6534c7daaf0ac4f7a8e1f74285da45f14bbee62276e3":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x58FB38,PHYS[0]))!="2137e21e3e62c7e89959b6b89d7d1252dcb386f11311af11e77b568b6c08a760" or sh(c._slice(b,PHYS[1],0x58FD18))!="232e226bd1ece2ee0d8a14abc3461651743ef4c987b46406fc2995154ed59a29":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls);providers=(EASY,RING,UART)
 if len(calls)!=24 or c._pair_digest(calls)!="39d11d6cd9242d5bb1bf97f90fcadee709c54f9e399cf057b90a45a9ff05ce3e" or set(ext)!=set().union(*providers):raise c.AuditError("call topology changed")
 if tuple(sum(ext[x] for x in group) for group in providers)!=(20,1,3):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=7 or c._pair_digest(entries)!="e74341a2a1df4093d4dc9d71d67c6ee1a97b5d724f79b8e2ab5d40b3f54099b9" or strict:raise c.AuditError("BL entry topology changed")
 if t.literal_references(b,0x58FCC8)!=[0x58FB8C,0x58FBD6,0x58FC28,0x58FC72]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":2,"ghidra_discovered_functions":2,"path_anchored_functions":2,"body_bytes":342,"physical_bytes":414,"outer_pool_bytes":72,"direct_body_calls":24,"internal_direct_body_calls":0,"external_direct_body_calls":24,"indirect_body_calls":0,"direct_bl_entry_sites":7,"stored_entry_pointers":0},"provider_boundary":{"easylogger_calls":20,"ring_buffer_calls":1,"first_party_uart_calls":3,"ring_buffer_commit_interval":["cda00e1efb815bad5100757f0d10d117f633ced6","190e30bebcec22d7311fd941179d70b4f439c441"],"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
