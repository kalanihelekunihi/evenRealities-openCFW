#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard_layout.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-dashboard-layout-function-map.tsv";CL=ROOT/"tools/manifests/g2-dashboard-layout-closure.tsv";PM=ROOT/"tools/manifests/g2-dashboard-layout-provider-map.tsv"
PINS={FM:"e9a0b65f97e32388492f981a3e7ae52d3a9880a1ac923c96ddf13a3793d81fcd",PM:"a052272dff31f673a2bdd1a741198c84d67ce0225fcd36d73469a512515da1d8",CL:"4f5988689120e3ed51431b98631a2dd7527e7e4bc44cfb4049b71afd641427e1"}
PHYS=(0x558030,0x55894C);PATH_CELL=0x5588B8
RAW_DATA_BL=(0x6D3170,0x558590)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x44B610}
FILE={0x474550,0x4745F4,0x47498C,0x474A76,0x474B02,0x474C66}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
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
 if len(F)!=11 or sum(r['source_path_anchor']=='yes' for r in rows)!=4:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2162 or sh(body)!="a7136e63708871fa9719ba0ac4fb77c22402a841d09a20c713d5d4af6756fb39" or len(ins)!=896 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="2534fb285a4fe351a0fd3795f40f9e7e2346b73b999880330dc6d7a477a69a2b" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=170 or sh(non)!="c63491d700793a858fe5ee3be923e1a82959fc100183b21354e66047c9b5d5d9" or sh(c._slice(b,*PHYS))!="8b356371d046e9c41411e43b8ac7099f230be4a01e1d1e1ba78ea8caadeb2a45":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="0e36208d61885723515be9bcd7b4563cd49c9bc33cfff2730776bce56b6154bf" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="ad4825220105afc88a31762fe941f7842d194196972348788f75843548c01c06":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,FILE)
 if len(calls)!=98 or sum(y in starts for x,y in calls)!=11 or c._pair_digest(calls)!="2b6d0e886a64177b472293cec847ea22c1a21f6a97df37c0d7de68a19ca0d940" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(75,4,8):raise c.AuditError("provider accounting changed")
 entries=[];strict=[];unknown=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:unknown.append((a,y))
 if len(entries)!=32 or sum(not(PHYS[0]<=s<PHYS[1]) for s,_ in entries)!=21 or c._pair_digest(entries)!="af93f145c06d8b418cb6dbe131018983e90da44314b36a870b4096bfa36ea5df" or unknown or strict!=[RAW_DATA_BL]:raise c.AuditError("BL ingress changed")
 if sh(c._slice(b,RAW_DATA_BL[0]-8,RAW_DATA_BL[0]+8))!="67193be1a3270fe468c1b14ae9e42e0095c2bc91860e492d4071b1d376c710d7" or RAW_DATA_BL[0]<0x6C0000:raise c.AuditError("raw data-window BL decode context changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];pseudo=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if stored or len(pseudo)!=1 or c._pair_digest(pseudo)!="6d7c7a5a7ea29d348711b723f93eeb5ffc7b43ef37e481a75b7e9b7224d6e396" or any(a%4==0 for a,v in pseudo):raise c.AuditError("stored entry closure changed")
 if cstring(b,0x6F2CC8)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_layout.c":raise c.AuditError("path changed")
 pairs=[(PATH_CELL,x) for x in t.literal_references(b,PATH_CELL)]
 if len(pairs)!=15 or c._pair_digest(pairs)!="9f26093411efcb2357eee2c82f118ee33978220f37cb50cfc13d41790188a428":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().replace("\\","/").endswith("dashboard/dashboard_layout.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\dashboard\dashboard_layout.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":11,"ghidra_discovered_functions":4,"restored_functions":7,"path_anchored_functions":4,"body_bytes":2162,"physical_bytes":2332,"noncode_bytes":170,"reachable_instructions":896,"direct_body_calls":98,"internal_direct_body_calls":11,"external_direct_body_calls":87,"indirect_body_calls":0,"direct_bl_entry_sites":32,"external_direct_bl_entry_sites":21,"stored_function_entry_pointers":0,"unaligned_stored_interior_pseudo_pointers":1,"raw_data_window_interior_bl_decodes":1,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":75,"iar_dlib_calls":4,"file_runtime_calls":8,"cmsis_freertos_calls":0,"freertos_kernel_calls":0,"new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
