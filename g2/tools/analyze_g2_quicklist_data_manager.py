#!/usr/bin/env python3
"""Fail-closed object/provider audit for quicklist_data_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-quicklist-data-manager-function-map.tsv";PM=ROOT/"tools/manifests/g2-quicklist-data-manager-provider-map.tsv";CL=ROOT/"tools/manifests/g2-quicklist-data-manager-closure.tsv"
PINS={FM:"fc21d8ca606a0fdd7f8411960849164c766e5633ad00eb8d18b03d183f1a3d16",PM:"9c46eb45ba5a354c427e278bf5573cec3525a6a507bf3ba3a735ea9222dcbbd3",CL:"23b00e6cd07a056147ce9ec024f23fa2da0038e97dc2b93a0ef3ddeb7c6c042f"}
PHYS=(0x58D51C,0x58DAE4);PATH_CELLS=(0x58D9C4,0x58DAD0)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};FIRST={0x44A1C6}
def sh(x):return hashlib.sha256(x).hexdigest()
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
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
 if len(F)!=3 or sum(r['source_path_anchor']=='yes' for r in rows)!=3:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=1350 or sh(body)!="957e5df95cf845d762ec1670613ab8040dc5768b228978d5fd728ebbcb5a5992" or len(ins)!=481 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="52c088ba13953f314fd60012f54723c00a87d1f3f1d1891957def6bf86884eb2" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=130 or sh(non)!="354b9b86779b0372779647fd047e35b31edcf279fd57d98a811999aeddd4569e" or sh(c._slice(b,*PHYS))!="af41f01594809e9b5f1dd36ede339dccdb948b000285797fe1bbe373f26d5b9a":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="98103a8acd56be83b4b7f66accdbcbe109f0c81d953e5b551ece843e39b5c53d" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="46e534f1e68376942fccaab048b26d371ac6942531f987ef2af9a5631b2f3ceb":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,FIRST)
 if len(calls)!=69 or sum(y in starts for x,y in calls)!=2 or c._pair_digest(calls)!="cf23522ebc56096676b18b75c684e3be40a4cf972e17bcab80f6052e9bd9eda7" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(60,5,2):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=4 or c._pair_digest(entries)!="26c990ef858da28681836e93e22eb3db586782af1b1417123d22ec1d505455db" or strict:raise c.AuditError("raw ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or interior:raise c.AuditError("stored/interior ingress changed")
 pairs=sorted((cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell))
 if len(pairs)!=12 or c._pair_digest(pairs)!="53c8058c7577a9c14fbf4a1492dff9abf39f8b0155336673c8f47d6d57b5f135":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("quicklist_data_manager" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\quicklist\quicklist_data_manager.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":3,"ghidra_discovered_functions":3,"restored_functions":0,"path_anchored_functions":3,"body_bytes":1350,"physical_bytes":1480,"noncode_bytes":130,"reachable_instructions":481,"direct_body_calls":69,"internal_direct_body_calls":2,"external_direct_body_calls":67,"indirect_body_calls":0,"direct_bl_entry_sites":4,"stored_function_entry_pointers":0,"raw_instruction_word_interior_collisions":0,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":60,"iar_dlib_calls":5,"first_party_calls":2,"cmsis_freertos_calls":0,"freertos_kernel_calls":0,"historical_quicklist_manager_commit":None,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
