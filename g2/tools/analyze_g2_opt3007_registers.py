#!/usr/bin/env python3
"""Fail-closed raw-image audit of the OPT3007 register-map initializer."""
import csv,hashlib,json,re,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-opt3007-registers-function-map.tsv";CL=ROOT/"tools/manifests/g2-opt3007-registers-closure.tsv";PM=ROOT/"tools/manifests/g2-opt3007-registers-provider-map.tsv"
PINS={FM:"31b30dc9653fa501c37ffe5052098aaf8efc4d070f7279daa0d1b7a00e188047",CL:"9f69fb7d0e51f6da70542ec7065df831440b910a5bc3a21111d4479fb5a28d5e",PM:"8a784bba12262ffd2033c2bff3583a4d0f0dc61635450bca39f66c0c80c957a4"}
F=((0x5135E0,0x513734),);PHYS=(0x5135E0,0x513748);POOL=(0x513734,0x513748);EASY={0x43CE9E,0x43D0CE,0x43D574}
DESCRIPTORS=((11,0,0),(15,12,0),(15,12,1),(11,11,1),(10,9,1),(8,8,1),(7,7,1),(6,6,1),(5,5,1),(4,4,1),(3,3,1),(2,2,1),(1,0,1),(15,12,2),(11,0,2),(15,12,3),(11,0,3),(15,0,0x7E),(15,0,0x7F))
MOV_RE=re.compile(r"r0, #(0x[0-9a-f]+|[0-9]+)$");STORE_RE=re.compile(r"r0, \[r4(?:, #(0x[0-9a-f]+|[0-9]+))?\]$")
def sh(x):return hashlib.sha256(x).hexdigest()
def recover_descriptor_bytes(ins):
 out=bytearray(57);seen=set();value=None
 for a,i in sorted(ins.items()):
  if a<0x51361C:continue
  if i.mnemonic=="movs":
   m=MOV_RE.fullmatch(i.op_str)
   if m:value=int(m.group(1),0)
  elif i.mnemonic.startswith("strb"):
   m=STORE_RE.fullmatch(i.op_str)
   if not m or value is None:raise c.AuditError("descriptor store pattern changed")
   offset=int(m.group(1),0) if m.group(1) else 0
   if offset>=len(out) or offset in seen:raise c.AuditError("descriptor offset changed")
   out[offset]=value;seen.add(offset)
 if seen!=set(range(57)):raise c.AuditError("descriptor coverage changed")
 return bytes(out)
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=1:raise c.AuditError("function inventory changed")
 row=rows[0];a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
 if (a,z)!=F[0] or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
 ins,calls,ind=d._recover_function(b,a,z);calls.sort()
 if c._uncovered(F[0],ins) or len(ins)!=139 or c._instruction_digest(sorted((x,i.size) for x,i in ins.items()))!="cfe6e0d14016fcdca743d8b46305fd31098133abc9334c3df1626815825e8ff8" or ind:raise c.AuditError("instruction closure changed")
 descriptor_bytes=recover_descriptor_bytes(ins)
 if tuple(tuple(descriptor_bytes[i:i+3]) for i in range(0,57,3))!=DESCRIPTORS:raise c.AuditError("register descriptor map changed")
 if sh(c._slice(b,*PHYS))!="3413758945a068997bbe9ed899112cf9b5954399fb088ee6e30215c8866023f8" or sh(c._slice(b,*POOL))!="fe506ad315d09f6f04ba78388c1b6731d7767a0941ddd41e8ffb260d461004b0":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x5135D2,PHYS[0]))!="39445f1943d17d5bf38df9d7b03bbd2d30a6ee429b9928166ab8b9b90b03ba63" or sh(c._slice(b,PHYS[1],0x513780))!="d2fdaade4c9e113442ba1a5ce61e4199285a5be349ab0f386eadeebd95943f4b":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls)
 if len(calls)!=5 or c._pair_digest(calls)!="0fe457f60501d1743d8049ec6da92e62b2fc719f2f5a196387b9ef040edf2f47" or set(ext)!=EASY or sum(ext.values())!=5:raise c.AuditError("call topology changed")
 entries=[];strict=[];interiors=set(range(a+2,z,2))
 for x in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,x)
  if y==a:entries.append((x,y))
  elif y in interiors:strict.append((x,y))
 if len(entries)!=2 or c._pair_digest(entries)!="838da3911681ed615eb840ff6831f0717be36ef8feaef2dd1497204c12f93927" or strict:raise c.AuditError("BL entry topology changed")
 if t.literal_references(b,0x51373C)!=[0x5135F6]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":["TI OPT3007 SBOS864 register specification"]},"surface":{"linked_functions":1,"ghidra_discovered_functions":1,"path_anchored_functions":1,"body_bytes":340,"physical_bytes":360,"outer_pool_bytes":20,"direct_body_calls":5,"internal_direct_body_calls":0,"external_direct_body_calls":5,"indirect_body_calls":0,"direct_bl_entry_sites":2,"stored_entry_pointers":0},"register_map":{"descriptor_count":19,"descriptor_bytes":57,"descriptors":[list(x) for x in DESCRIPTORS],"datasheet":"TI SBOS864, August 2017","public_code_match":False},"provider_boundary":{"easylogger_calls":5,"easylogger_commit":"a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
