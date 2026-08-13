#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for EvenHub/evenhub_main.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-evenhub-main-function-map.tsv";PM=ROOT/"tools/manifests/g2-evenhub-main-provider-map.tsv";CL=ROOT/"tools/manifests/g2-evenhub-main-closure.tsv"
PINS={FM:"d12837dd65cd1902427ca44c9240e0ba647aba3207f54553a539a7b4c839a93c",PM:"3565f28659092620e89fe243bfc264e52ab87cb817e284b4f493922ab4649776",CL:"a28adeb5b311a75fe04022c58793f4dd880f455f7783347aacbedb828d29110f"}
PHYS=(0x4E0CCE,0x4E1A48);PATH_CELLS=(0x4E1460,0x4E19E0);RAW_PSEUDO=(0x6312BE,0x4E1180);RAW_WORD=(0x64BA02,0x4E0E1F)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4,0x47CC60};LVGL={0x441488};CMSIS={0x4490CC};NANOPB={0x48EB32};HEAP={0x474CD2,0x474D16}
FIRST={0x443484,0x4434D0,0x45A568,0x45A570,0x46410A,0x4641B6,0x464C36,0x465480,0x4935FE,0x493D02,0x493FA8,0x494610,0x494834,0x494BEC,0x496544,0x4D9B34,0x4D9D9A,0x4D9F6E,0x4DA078,0x4DA16A,0x4DA720,0x4DA834,0x4E0CA0,0x4E0CAA,0x54F380,0x54F50E,0x5FA0A4}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/lvgl/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="344c7c318047b7348e1be8572a9fd4260c251cfa":raise c.AuditError("LVGL changed")
 if json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
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
 if len(F)!=5 or sum(r['source_path_anchor']=='yes' for r in rows)!=3:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=3130 or sh(body)!="33242c045ce409a312c012fb02e426943bc4f235a373d017e3ace22a795e3ec0" or len(ins)!=1193 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="db7ce7cb52ef8e80fa93eec2787253c9a0971c846d145466f94a11adcf425793" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=320 or sh(non)!="5cac69afc3a2e890adaf0f95f6d47508073a5b7af5619a4eda33a2a2896a1875" or sh(c._slice(b,*PHYS))!="0889559d01755e757ba19f70259c01b20cdeb18ada464042196ffe854a5bebac":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="691e71cc3c3635af88e4b974147bc2af2398cb8a162d2d27d24051c9c47bd547" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="177f8857f078f79ea314f256f3fe8013df55221ee64b7e4e9edc5da064f32a05":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,CMSIS,NANOPB,HEAP,FIRST)
 if len(calls)!=181 or sum(y in starts for x,y in calls)!=1 or c._pair_digest(calls)!="57d927d52239f18e56f0e07a61829c8a52c5bf519b39fdd4f849cc4cad79c7c3" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(120,6,2,2,3,2,45):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=3 or c._pair_digest(entries)!="18d5ce69ebdfb1752e0f4b10de5be495cbb902724e56a239b40bd984daab2dc0" or strict!=[RAW_PSEUDO]:raise c.AuditError("raw ingress changed")
 if not 0x600FAA<=RAW_PSEUDO[0]<0x794324 or sh(c._slice(b,0x6312B0,0x6312D0))!="203f11e7d6054084d6c25a0df0106acc0422b8e22f3812d89e08351328a7aa03" or c._slice(b,RAW_PSEUDO[0],RAW_PSEUDO[0]+4)!=bytes.fromhex("aff65fff"):raise c.AuditError("raw resource pseudo-BL proof changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=2 or c._pair_digest(stored)!="ec420d2cfc6c4e2bb8e432a6afd968aad022471d8b538511735b5161770d9615" or interior!=[RAW_WORD]:raise c.AuditError("stored entry closure changed")
 if not 0x600FAA<=RAW_WORD[0]<0x794324 or RAW_WORD[0]%4!=2 or sh(c._slice(b,0x64B9F8,0x64BA0C))!="1090637b4845a7b093893e28831307cb43893398c937d81868a2e31b8c965076" or c._slice(b,0x64BA00,0x64BA06)!=bytes.fromhex("002f1f0e4e00"):raise c.AuditError("unaligned resource-word collision proof changed")
 if cstring(b,0x702988)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_main.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=24 or c._pair_digest(pairs)!="61fd2530557c777cee730f0acbc80936c9fb91bb0284b736bf8ccbefb841a7c4":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("evenhub_main" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\EvenHub\evenhub_main.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":5,"ghidra_discovered_functions":4,"restored_functions":1,"path_anchored_functions":3,"body_bytes":3130,"physical_bytes":3450,"noncode_bytes":320,"reachable_instructions":1193,"direct_body_calls":181,"internal_direct_body_calls":1,"external_direct_body_calls":180,"indirect_body_calls":0,"direct_bl_entry_sites":3,"stored_function_entry_pointers":2,"raw_noncode_pseudo_bl_sites":1,"raw_unaligned_interior_word_collisions":1,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":120,"iar_runtime_calls":6,"lvgl_calls":2,"cmsis_freertos_calls":2,"nanopb_calls":3,"heap_wrapper_calls":2,"first_party_calls":45,"historical_evenhub_main_commit":None,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
