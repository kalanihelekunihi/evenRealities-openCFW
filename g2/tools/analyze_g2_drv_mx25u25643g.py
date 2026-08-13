#!/usr/bin/env python3
"""Fail-closed object/provider audit for driver/flash/drv_mx25u25643g.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-drv-mx25u25643g-function-map.tsv";CL=ROOT/"tools/manifests/g2-drv-mx25u25643g-closure.tsv";PM=ROOT/"tools/manifests/g2-drv-mx25u25643g-provider-map.tsv"
PINS={FM:"86c541134394f609a4515dd0b66fd6e071ea1b3a06f10201e5cd0b694d978690",CL:"635e5b4ea162441d46f60539b27cf12abb1f8f8e45f99c4fce6b34f1e2a22535",PM:"291feb147357f720c2748caa4ddeac7a9318cf8d4e17000d29e04b3e306e9db9"}
PHYS=(0x46F4A4,0x471164);PATH_CELLS=(0x4700A4,0x470A78,0x4710E0)
EASY={0x43CE9E,0x43D0CE,0x43D574};AMBIQ={0x480EEE,0x4C0812,0x4C08A8,0x4C099C,0x4C0E1E,0x4C0EA8,0x4C0F24,0x4C0F78,0x4C2098,0x4C2328,0x4C2392,0x4C23DE,0x4C240E,0x4C26E0,0x4C32B4};CMSIS={0x44906C,0x449376,0x44971C,0x4497B6,0x44981C};NANOPB={0x48949C};IAR={0x439C04,0x43BB00};RUNTIME={0x4733EE,0x473934};DELAY={0x4910F4,0x491102}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if json.loads((ROOT/"third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="5efc0228528a8adce5eae0d226fac85d2551eb3b":raise c.AuditError("AmbiqSuite changed")
 if json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("CMSIS-FreeRTOS changed")
 if json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("nanopb changed")
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
 if len(F)!=40 or sum(r['source_path_anchor']=='yes' for r in rows)!=21:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if len(body)!=6726 or sh(body)!="c2d9d0353d648043c16b976f20d28c350959296638a30d543dc7f4137164cd66" or len(ins)!=2479 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="600043788fe3aa6fab1f562ef990d45ee9a0f620432cbb1d0fb0f8f190be03b4" or ind:raise c.AuditError("instruction closure changed")
 mask=bytearray(PHYS[1]-PHYS[0])
 for a,i in ins.items():
  for j in range(i.size):mask[a-PHYS[0]+j]=1
 rawphys=c._slice(b,*PHYS);non=bytes(v for v,m in zip(rawphys,mask) if not m)
 if len(non)!=634 or sh(non)!="315cadb6713ad4f24a2946aa04287513fd3ed36a67097baa8f5ef78baa389f87" or sh(rawphys)!="0d66d02bcbd780a35001183e7cef9b6d1bc5dca054d73baf3d1d14fb0fa97f9d":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="2073a07530b3b3c8423054c6ad3b5a8342e416ceec8573d760bfc875ce8cf003" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="e7a10ab37b62483322ce274a7d47bba8019021d55bdbb62e2fa14c4c5439ba64":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,AMBIQ,CMSIS,NANOPB,IAR,RUNTIME,DELAY)
 if len(calls)!=386 or sum(y in starts for x,y in calls)!=89 or c._pair_digest(calls)!="5a00ed76995a1bcbaac334fbe2744fef719b497a98021153aee63a61c14df115" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(230,31,5,3,7,16,5):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=126 or c._pair_digest(entries)!="e3719689c05146b470b077df44d10b8a0388090f2fac68f4d9ff73e0013fb591" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=[(0x438094,0x46F4EB),(0x6C11A0,0x470029),(0x79370B,0x4709C9),(0x793713,0x47075D)]:raise c.AuditError("stored entries changed")
 if cstring(b,0x70258C)!=r"D:\01_workspace\s200_ap510b_iar_git\driver\flash\drv_mx25u25643g.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=46 or c._pair_digest(pairs)!="70683326e619ae3bb6618d6e2c9dce0d1f8010629baf907b36d5c29b060003aa":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any(x.get("path","").lower().endswith("drv_mx25u25643g.c") for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"driver\flash\drv_mx25u25643g.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":40,"ghidra_discovered_functions":21,"restored_functions":19,"path_anchored_functions":21,"body_bytes":6726,"physical_bytes":7360,"noncode_bytes":634,"reachable_instructions":2479,"direct_body_calls":386,"internal_direct_body_calls":89,"external_direct_body_calls":297,"indirect_body_calls":0,"direct_bl_entry_sites":126,"stored_entry_pointers":4,"strict_interior_ingress":0},"behavior":{"mx25_command_and_status_flow":True,"quad_and_serial_mode_switching":True,"littlefs_read_prog_erase_ports":True,"ambiq_mspi_and_gpio_transport":True,"cmsis_locking_and_completion":True},"provider_boundary":{"easylogger_calls":230,"ambiqsuite_calls":31,"cmsis_freertos_calls":5,"shared_nanopb_initializer_calls":3,"iar_dlib_calls":7,"source_owned_runtime_calls":16,"source_owned_delay_calls":5,"ambiqsuite_commit":"5efc0228528a8adce5eae0d226fac85d2551eb3b","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
