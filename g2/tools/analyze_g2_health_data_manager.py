#!/usr/bin/env python3
"""Fail-closed object/provider audit for health_data_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-health-data-manager-function-map.tsv";PM=ROOT/"tools/manifests/g2-health-data-manager-provider-map.tsv";CL=ROOT/"tools/manifests/g2-health-data-manager-closure.tsv"
PINS={FM:"6e850bd713482629f98fa8aff0f7c263eb22f11b0e884d1a1d1a3c7278865284",PM:"ec85e7940ba073dc806224fed24792b021edee41f942c2d66e5f3a1bdf7481f9",CL:"b4a67632e1c7f2e55274304a9b2a38f32e0197a874506095496e79a6ae086e55"}
PHYS=(0x5597F0,0x55A350);PATH_CELLS=(0x559FAC,0x55A30C);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};HEALTH={0x4FFC32,0x4FFC90}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
 iar=(ROOT/"docs/research/iar-dlib-runtime-census.md").read_text()
 if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:raise c.AuditError("IAR changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=10 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2644 or sh(body)!="050ec6e745b00b6d6cfd37b83e2283415053a3f7e486e7bdff3a59ddccf541f4" or len(ins)!=976 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="41b051dcd8a6aa9d7322e196e189090968bd1e5dd6f49ffcd21657fa49fb9df4" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=268 or sh(non)!="243baf3a6d20197747a4cff17cb20485fa07895c4a267566fb134e8a493d37ca" or sh(c._slice(b,*PHYS))!="44352a771275d97318b726f9525fbff941a6f11bdc761736e0317a407ca3b2ae":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="260a519ad8da8666c618201c1a50a5ade32d8153dd491349f4e261e3eec761da" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="5cbaf0bff77f2af89d0f87730938566cc5456c30ce660918a34d10379e48581d":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,HEALTH)
 if len(calls)!=149 or sum(y in starts for x,y in calls)!=13 or c._pair_digest(calls)!="76897902ad5c523275572a03d364a4bdcf66ef46351845d83242087cacef47fd" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(120,6,10):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!="361456eea75ebc902cdaee6008b33e3956f575fc91d9641d218b536f179e4f73" or strict:raise c.AuditError("raw ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or interior:raise c.AuditError("stored entry closure changed")
 if cstring(b,0x6F3E00)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\health\health_data_manager.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=24 or c._pair_digest(pairs)!="f01b62d30614e6314d703baf8b8bda5204c4d5d1b1273ffd6a7602d0303e01e4":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("health_data_manager" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\health\health_data_manager.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":10,"ghidra_discovered_functions":9,"restored_functions":1,"path_anchored_functions":5,"body_bytes":2644,"physical_bytes":2912,"noncode_bytes":268,"reachable_instructions":976,"direct_body_calls":149,"internal_direct_body_calls":13,"external_direct_body_calls":136,"indirect_body_calls":0,"direct_bl_entry_sites":18,"stored_function_entry_pointers":0,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":120,"iar_runtime_calls":6,"closed_health_lock_calls":10,"direct_cmsis_freertos_calls":0,"historical_health_manager_commit":None,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
