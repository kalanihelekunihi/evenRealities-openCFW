#!/usr/bin/env python3
"""Fail-closed provider audit for conversate/conversate_tag_data.c."""
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-conversate-tag-data-function-map.tsv";CL=ROOT/"tools/manifests/g2-conversate-tag-data-closure.tsv";PM=ROOT/"tools/manifests/g2-conversate-tag-data-provider-map.tsv"
PINS={FM:"ebf5ea63030b01e701e4ae23ca3974dba0beccfb437b6899d8fbba3466736998",CL:"f26d478f5e3b484d1e453ff9f3a23eb52968c65bfe95733ae0e390829e03c775",PM:"937ee5f53e56d9b92ffad6ab13ac8f98ce386c7c299d072e5e7c5199252af889"}
PHYS=(0x595F4C,0x596A88);EASY={0x43CE9E,0x43D0CE,0x43D574};HEAP={0x474CD2,0x474D16};IAR={0x439BE4,0x43C0E4,0x44A43C}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
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
 if len(F)!=12 or sum(r['source_path_anchor']=='yes' for r in rows)!=9:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2726 or sh(body)!="a52f1f0d81b0bf3778a303f0afdc2e3ee52c3d225f8077990904658046d59dbc" or len(ins)!=1043 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="18cda14cb816384d326c3234ee9fa8185ac4d2a499bf27d88abebf8b2b1b1df0" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=150 or sh(non)!="8e2dc645506c17c986c8de6a813b176585ebcdbacd62a4bed5e4e686fe95d4fc" or sh(c._slice(b,*PHYS))!="8d9a54f28709b16724306650f3903e86bd170e2c046bfc1cac4fddca1412c3e7":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="4d3850af66e25c19f6aaf16d25e89ec1ffc3dec7e7d7d2861c6d768b22701b19" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="3c97953b2050533d9d42de82e2c607e3a3fd58e91c7d154fefc0a45bab56656f":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,HEAP,IAR)
 if len(calls)!=160 or sum(y in starts for x,y in calls)!=5 or c._pair_digest(calls)!="70bb5764d52826fe61c7a51cce3d9f5da9194d4e48d67a3955a4356f3c5760fc" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(140,8,7):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!="d287839bbb5ec9456a675f0bfd7b8dec9c012ab513d5b29b36b8c3d54c38dfd7" or strict:raise c.AuditError("ingress changed")
 if cstring(b,0x6EC618)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_tag_data.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in (0x5967B0,0x596A88) for x in t.literal_references(b,cell)]
 if len(pairs)!=28 or c._pair_digest(pairs)!="33e10320cbd9d47921937c06daa122e56d1397acdbf2d07e04d14cc6a858e219":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("conversate_tag_data" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\conversate\conversate_tag_data.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":12,"restored_functions":3,"path_anchored_functions":9,"body_bytes":2726,"physical_bytes":2876,"noncode_bytes":150,"reachable_instructions":1043,"direct_body_calls":160,"internal_direct_body_calls":5,"external_direct_body_calls":155,"indirect_body_calls":0,"direct_bl_entry_sites":18,"strict_interior_ingress":0},"behavior":{"tag_list_allocation":True,"tag_insert_delete_and_lookup":True,"text_copy_and_lifecycle":True},"provider_boundary":{"easylogger_calls":140,"source_owned_heap_wrapper_calls":8,"iar_dlib_calls":7,"nanopb_calls":0,"json_calls":0,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
