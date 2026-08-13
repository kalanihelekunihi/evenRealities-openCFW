#!/usr/bin/env python3
"""Fail-closed provider audit for platform/service/DFU/service_em9305_dfu.c."""
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-service-em9305-dfu-function-map.tsv";CL=ROOT/"tools/manifests/g2-service-em9305-dfu-closure.tsv";PM=ROOT/"tools/manifests/g2-service-em9305-dfu-provider-map.tsv"
PINS={FM:"092681d29d9f3172886aead35d9f3b203013a058d748f62a27bee344fa587982",CL:"418959a32672c14d92d512e483e5f312f807729b0fc53bc359fba20a60727a8a",PM:"1675c3629cee93954d1f7f93611d3320735d141ecb0aacb34e0070fe0b8e0fee"}
PHYS=(0x52F442,0x52FF4C);EASY={0x43CE9E,0x43D0CE,0x43D574};RUNTIME={0x474550,0x4745F4,0x474634,0x474CD2,0x474D16};IAR={0x439BE4,0x43C0E4};INIT={0x48949C};FIRST={0x52F3A0,0x52F3F8}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
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
 if len(F)!=7 or sum(r['source_path_anchor']=='yes' for r in rows)!=6:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=2802 or sh(body)!="1e33c7f52d6879c08ff7c0a5d5dd87c90627465d55507040e439d9e4ac6df3fa" or len(ins)!=1062 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="f0a4d17513d90868ab117019df3ee85e40ff1394bc39fd334e814379c99c1be4" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=24 or sh(non)!="dc01eb87570b530c16d419d23ad97f86bc0d0fef4fa872e6e931a181098a2d79" or sh(c._slice(b,*PHYS))!="52d7fdc8334661d60c6cb3c5784a4fe0022d42ff05ca2da1e3b9359025ee289d":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="1fe2dd8b7dcf39f1ee5e8f8790262071dc6fb09d7e72d25f2c731987b2a9af45" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="e6ad99a3bba78d83680131b3871aa72c329626bc0eab23aa0a5ddde31cfea91b":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,RUNTIME,IAR,INIT,FIRST)
 if len(calls)!=156 or sum(y in starts for x,y in calls)!=4 or c._pair_digest(calls)!="328fdccbb79a06a7b49cfdd41306ca7440d3a530c10738f106e4dd737f3f6184" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(125,18,4,1,4):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=7 or c._pair_digest(entries)!="5c0bb055c4d6f529e29ba2faba778cf98afdb7ead995c5fc4dbb5e92026cabf0" or strict:raise c.AuditError("ingress changed")
 if cstring(b,0x6EF818)!=r"D:\01_workspace\s200_ap510b_iar_git\platform\service\DFU\service_em9305_dfu.c":raise c.AuditError("path changed")
 refs=t.literal_references(b,0x52FF4C)
 if len(refs)!=25 or c._pair_digest([(0x52FF4C,x) for x in refs])!="e4b1c7e952f8d03006665b74e23f87cf94372ef42071125ead31a6adebbd46ea":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("service_em9305_dfu" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"platform\service\DFU\service_em9305_dfu.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":7,"restored_functions":1,"path_anchored_functions":6,"body_bytes":2802,"physical_bytes":2826,"noncode_bytes":24,"reachable_instructions":1062,"direct_body_calls":156,"internal_direct_body_calls":4,"external_direct_body_calls":152,"indirect_body_calls":0,"direct_bl_entry_sites":7,"strict_interior_ingress":0},"behavior":{"firmware_file_streaming":True,"dfu_state_and_status_handling":True,"chunk_buffer_lifecycle":True,"first_party_transport_dispatch":True},"provider_boundary":{"easylogger_calls":125,"source_owned_file_heap_calls":18,"iar_dlib_calls":4,"shared_nanopb_initializer_calls":1,"first_party_calls":4,"direct_em9305_packetcraft_calls":0,"nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
