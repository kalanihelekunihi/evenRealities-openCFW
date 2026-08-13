#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard_data_process.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-dashboard-data-process-function-map.tsv";CL=ROOT/"tools/manifests/g2-dashboard-data-process-closure.tsv";PM=ROOT/"tools/manifests/g2-dashboard-data-process-provider-map.tsv"
PINS={FM:"de16103e258fcc457cd7c626dc4a57db560bc765e5391ead0102b053148b659b",CL:"3b1f75c109cbd2898b2c544721287e1881cd3cf2078569b2244caf74b2c0f3c2",PM:"16e49d7c3e5378d901834a402b01f9906ca35873f82cab7fe83368a3c7c8cba3"}
PHYS=(0x4FE0AA,0x4FF8E4);PATH_CELLS=(0x4FE2FC,0x4FEEE4,0x4FF4A4,0x4FF8A4);ISLAND=(0x4FEC02,0x4FEC14)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4,0x44B5A0};NANOPB={0x48949C,0x48F49C,0x490120,0x4905F4,0x490C32};CMSIS={0x4490CC,0x4497B6,0x44981C};FREERTOS={0x454B4C}
FIRST={0x443484,0x4434D0,0x45A570,0x464BB2,0x464F76,0x475014,0x475B14,0x475C1A,0x4FD93C,0x4FDA24,0x4FDAD4,0x4FDD6E}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
 cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());kernel=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text())
 if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or kernel["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c":raise c.AuditError("RTOS changed")
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
 if len(F)!=14 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 decoder=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS)
 island=list(decoder.disasm(c._slice(b,*ISLAND),ISLAND[0]));ins.update({i.address:i for i in island})
 uncovered=[x for x in uncovered if x!=ISLAND];calls.sort();ind.sort()
 if uncovered or len(island)!=9 or len(body)!=5706 or sh(body)!="adfe92572c80465f075494d2485ea103476c13e9f68686639e5558259e6e9128" or len(ins)!=2143 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="14d687d7174d9d3619abd4c09a26294941f2738b1dc5b62c641ccd1f59a8b632" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=496 or sh(non)!="d7f8aa6590d8c87eb66ea2b4c1f5852aa7f7198234404f4dc670379e802ecec5" or sh(c._slice(b,*PHYS))!="a6db691772be8638127ba3435980a3a5726e9832832285e2d451a99b7501a0f9":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="27c532640da93620873b0f514569a5724def2e40ccdb558712656718dfbd349b" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="f510f7dab55068b9cdd7c0e85ee4554b3e43228dd520fcf17e0790199de31910":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,NANOPB,CMSIS,FREERTOS,FIRST)
 if len(calls)!=262 or sum(y in starts for x,y in calls)!=7 or c._pair_digest(calls)!="05dc45fc65cc393a9d3eeb4990cc0d96d8198cf67b025a63926dd07c587969b8" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(170,32,19,4,1,29):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=23 or c._pair_digest(entries)!="6342febd564363ae856988c77ae7c95a016d2c6f7dc36af3861afdea6a8f071b" or strict:raise c.AuditError("BL ingress changed")
 words=[struct.unpack_from('<I',b,o)[0] for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 if any(v in enc for v in words) or any((v&1) and (v&~1) in inter for v in words):raise c.AuditError("stored entry appeared")
 if cstring(b,0x6DA4E4)!=r"D:\01_workspace\s200_ap510b_iar_git\platform\protocols\dashboard_service\dashboard_data_process.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=37 or c._pair_digest(pairs)!="c5714bd26dea14bb533bfe84583d15096aaafffb4ace80433b059ff6549f2c33":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("dashboard_data_process" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"platform\protocols\dashboard_service\dashboard_data_process.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":14,"ghidra_discovered_functions":10,"restored_functions":4,"path_anchored_functions":7,"body_bytes":5706,"physical_bytes":6202,"noncode_bytes":496,"reachable_instructions":2143,"linear_dispatch_island_instructions":9,"direct_body_calls":262,"internal_direct_body_calls":7,"external_direct_body_calls":255,"indirect_body_calls":0,"direct_bl_entry_sites":23,"stored_function_entry_pointers":0,"strict_interior_ingress":0},"behavior":{"dashboard_record_decode_encode":True,"role_aware_data_dispatch":True,"record_allocation_and_copy":True,"shared_state_synchronization":True,"dashboard_state_update":True},"provider_boundary":{"easylogger_calls":170,"iar_dlib_calls":32,"nanopb_calls":19,"cmsis_freertos_calls":4,"freertos_calls":1,"first_party_calls":29,"nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
