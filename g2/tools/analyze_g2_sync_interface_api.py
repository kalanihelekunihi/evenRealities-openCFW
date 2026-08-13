#!/usr/bin/env python3
"""Fail-closed object/provider audit for framework/sync/sync_interface_api.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-sync-interface-api-function-map.tsv";CL=ROOT/"tools/manifests/g2-sync-interface-api-closure.tsv";PM=ROOT/"tools/manifests/g2-sync-interface-api-provider-map.tsv"
PINS={FM:"2d784afd63a9cd42525aab2646bdb0463f4b3627322a0ee8475de04342caa60d",CL:"bac3ed9cf3fd42a7752ef4e09ef71bfe4c91bc3eef12a91efdf48f0bf9a96031",PM:"8c7137d4eb720f4474ed663fd42978acb8301be4c2552f9c6f58b2418f735fcf"}
PHYS=(0x4646F0,0x466010);PATH_CELLS=(0x4651B4,0x465D60,0x465FF4)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x449376,0x4495E4,0x449ABE};FREERTOS={0x5FA0A4};IAR={0x439BE4,0x43C0E4};HEAP={0x474CD2,0x474D16};FIRST={0x45A568}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
 if "deff9ab509341f264addbd3c8ada533678591905" not in (ROOT/"third_party/tlsf/README.openCFW.md").read_text():raise c.AuditError("TLSF changed")
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
 if len(F)!=13 or sum(r['source_path_anchor']=='yes' for r in rows)!=13:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if len(body)!=6136 or sh(body)!="b7bed2187643568dcc9510747dcad28ceb6d9ba97a147d5e09e8d2afa2a14bc6" or len(ins)!=2350 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="079f372c169bfa5bdb15c8eb99a2930de943f6c8feabb9d540f09c1fda6ca191" or ind:raise c.AuditError("instruction closure changed")
 mask=bytearray(PHYS[1]-PHYS[0])
 for a,i in ins.items():
  for j in range(i.size):mask[a-PHYS[0]+j]=1
 rawphys=c._slice(b,*PHYS);non=bytes(v for v,m in zip(rawphys,mask) if not m)
 if len(non)!=296 or sh(non)!="d3d36c97d35cff65779b409bc76de407aa400f2be26a9ed5a481c2c895f89ba0" or sh(rawphys)!="1168ab1698fee199840a0d13ac6201bb68fed8fe9b906e9741679908db26ac74":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="e2a36f66e110001c119616c234eb7d5fa6a38bc818918985db5efda17c94595e" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="7cade0df38e03e7bc0d0cd724310666c7a5e5e26cc7b83060b996dfead7b316d":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,FREERTOS,IAR,HEAP,FIRST)
 if len(calls)!=353 or sum(y in starts for x,y in calls)!=20 or c._pair_digest(calls)!="acfb662d9db1b766ffb622d19a428c2b9793118d3d493e8f6ef1ccb1df4bf2ab" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(255,17,9,13,33,6):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=329 or c._pair_digest(entries)!="9979fbcd5d82a28a3e9f9b8ab271b3cc64eb1b5886b45b217984356047cec2b6" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x4C9C68,0x464D1D)]:raise c.AuditError("stored entries changed")
 if cstring(b,0x6FD6AC)!=r"D:\01_workspace\s200_ap510b_iar_git\framework\sync\sync_interface_api.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=51 or c._pair_digest(pairs)!="8d817206ae4580ec5403a6c3b1cf952bd412d9cbb97c30bd06e042c139bbeb8c":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().endswith("sync_interface_api.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"framework\sync\sync_interface_api.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":13,"ghidra_discovered_functions":13,"restored_functions":0,"path_anchored_functions":13,"body_bytes":6136,"physical_bytes":6432,"noncode_bytes":296,"reachable_instructions":2350,"direct_body_calls":353,"internal_direct_body_calls":20,"external_direct_body_calls":333,"indirect_body_calls":0,"direct_bl_entry_sites":329,"stored_entry_pointers":1,"strict_interior_ingress":0},"behavior":{"role_gated_sync_submission":True,"cmsis_event_and_queue_transport":True,"source_owned_message_lifecycle":True,"stored_api_callback":True},"provider_boundary":{"easylogger_calls":255,"cmsis_freertos_calls":17,"freertos_assert_calls":9,"iar_dlib_calls":13,"source_owned_heap_wrapper_calls":33,"first_party_calls":6,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
