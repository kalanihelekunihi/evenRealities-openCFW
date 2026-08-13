#!/usr/bin/env python3
"""Fail-closed object/provider audit for dashboard_watchface_layout4.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-dashboard-watchface-layout4-function-map.tsv";CL=ROOT/"tools/manifests/g2-dashboard-watchface-layout4-closure.tsv";PM=ROOT/"tools/manifests/g2-dashboard-watchface-layout4-provider-map.tsv"
PINS={FM:"5e462358cb0e319d703d9015f3c8efa26758acd6bb958c4521dd91212641fb08",CL:"13e995940fcab3d0c3b92a5b95bccfedc389ffe3a90730bb16abb806aa7f3bbb",PM:"393366c1143b8f0bb1e5ad43106b517a3430b64b88a18f96830cb88c931a9d45"}
PHYS=(0x5BABA6,0x5BBDA4);PATH_CELLS=(0x5BB2D4,0x5BBCEC);PSEUDO=(0x4C816C,0x5BB770,0x4C816A)
EASY={0x43CE9E,0x43D0CE,0x43D574}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43FDDA,0x44104C,0x4411E4,0x441254,0x44127E,0x44129E,0x44131C,0x44133A,0x441378,0x441386,0x44140E,0x44142E,0x44143E,0x44146A,0x44D7B8,0x498668,0x498680,0x499416,0x49942E}
IAR={0x43C0E4,0x44B5A0,0x44B728};AMBIQ={0x4C2392,0x4C23DE,0x4C240E}
FIRST={0x44A1C6,0x46650C,0x47D8CE,0x47D9C4,0x47D9CC,0x48BA78,0x48BA92,0x49C5BC,0x509F8E,0x577D08,0x59CF1A,0x5BAB2C,0x5BAB76,0x5BBDA4}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
 if json.loads((ROOT/"third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="5efc0228528a8adce5eae0d226fac85d2551eb3b":raise c.AuditError("AmbiqSuite changed")
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
 if len(F)!=23 or sum(r['source_path_anchor']=='yes' for r in rows)!=3:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=4184 or sh(body)!="bc618986eda768267255e6b9e1fd5c3804556d088dbef97572cbfc70682b3342" or len(ins)!=1583 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="1e218efcf922d3c9d6cb799b04292dfe6f0a6a67695fcca45c0e0aaa625f9d17" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=422 or sh(non)!="6e0cc27e6c3716b8ba793b533ecf35c02b31283ee5fd21ee6d6297daea06faaa" or sh(c._slice(b,*PHYS))!="c603591ab318e8048e0308c61ba04308583bff4eadee966c0113b7a04eff5a28":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="885efae89d825e618f7c8b4161661e0a419ce441bfe99bedaa504f0220349559" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="d3d3efd0eb00786f8d51265664d4f16520ca7183f6061ebefc369c6d25f3d400":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,AMBIQ,FIRST)
 if len(calls)!=248 or sum(y in starts for x,y in calls)!=18 or c._pair_digest(calls)!="b837c4f3f8fe78e38c1a833be3004cde1762b9f3e0f1e48b6ef7d77d90cc0660" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(60,122,14,3,31):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!="bc33283d91f89bef44bdc12c92a4fed2c716b4c1d6190d81b84dc9f09bdfeabb" or strict!=[(PSEUDO[0],PSEUDO[1])]:raise c.AuditError("raw ingress changed")
 decoder=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);i=next(decoder.disasm(c._slice(b,PSEUDO[2],PSEUDO[2]+4),PSEUDO[2]),None)
 if i is None or i.size!=4 or i.mnemonic!="sdiv" or PSEUDO[0]!=PSEUDO[2]+2:raise c.AuditError("pseudo-BL overlap proof changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=11 or c._pair_digest(stored)!="8f6549589caef0fe2e58606a22d32cdd4fdc5b160b41b29a1a41ba2a89c16ca3" or interior:raise c.AuditError("stored entry closure changed")
 if cstring(b,0x6E73E4)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout4.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=12 or c._pair_digest(pairs)!="340bf6564972e076fd6bc0240ac525baefdf1e44cad47611c88dc1fee20289d1":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("dashboard_watchface_layout4" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\dashboard\dashboard_watchface_layout4.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":23,"ghidra_discovered_functions":3,"restored_functions":20,"path_anchored_functions":3,"body_bytes":4184,"physical_bytes":4606,"noncode_bytes":422,"reachable_instructions":1583,"direct_body_calls":248,"internal_direct_body_calls":18,"external_direct_body_calls":230,"indirect_body_calls":0,"direct_bl_entry_sites":18,"stored_function_entry_pointers":11,"raw_overlapping_pseudo_bl_sites":1,"strict_interior_ingress":0},"behavior":{"layout_configuration_validation":True,"time_battery_and_ble_widget_rendering":True,"lvgl_object_construction":True,"stored_lifecycle_callbacks":True,"mspi_cleanup_callback":True},"provider_boundary":{"easylogger_calls":60,"lvgl_calls":122,"iar_dlib_calls":14,"ambiqsuite_calls":3,"first_party_calls":31,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","ambiqsuite_commit":"5efc0228528a8adce5eae0d226fac85d2551eb3b","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
