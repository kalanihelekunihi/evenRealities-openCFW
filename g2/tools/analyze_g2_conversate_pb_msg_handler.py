#!/usr/bin/env python3
"""Fail-closed object/provider audit for conversate_pb_msg_handler.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-conversate-pb-msg-handler-function-map.tsv";PM=ROOT/"tools/manifests/g2-conversate-pb-msg-handler-provider-map.tsv";CL=ROOT/"tools/manifests/g2-conversate-pb-msg-handler-closure.tsv"
PINS={FM:"6c1a7dfbc07b92d66e7b9e48e7f2bc30dd1171b3b15d562ed3046adbf438476b",PM:"aa37ab5b1a165b958ae315c8fa100dab2f01bd0e6095d2fe98a08c758cc46abf",CL:"342fe332f4730cac6199a8c94dde297aba806c6c079e76961e6ea01f594f2e2b"}
PHYS=(0x5B48F8,0x5B57AC);PATH_CELLS=(0x5B52D4,0x5B56D0);DISPATCH_TABLE=0x727BC0
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4};LVGL={0x44120E,0x44121C,0x44122A,0x441238};NANOPB={0x48EB32}
FIRST={0x44A1C6,0x45A568,0x45A8EE,0x54F380,0x54F50E,0x5897E0,0x59619E,0x596360,0x5B02E4,0x5B133C,0x5B16D0,0x5B16DC,0x5B41BE,0x5B4378,0x5B43EE,0x5B44D8,0x5B476A,0x5B57AC}
HANDLERS={0x5B4A90,0x5B4CC8,0x5B4D10,0x5B4DBA,0x5B4E98,0x5B4F72,0x5B5150,0x5B52E0,0x5B5428,0x5B55B4}
INTERIOR=[(0x64AA03,0x5B4DFF),(0x6A41EC,0x5B51FF)]
def sh(x):return hashlib.sha256(x).hexdigest()
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
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
 if len(F)!=15 or sum(r['source_path_anchor']=='yes' for r in rows)!=5:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=3440 or sh(body)!="55857b6ed7e544c8eb50de51628f9652ebb4f82be9fb1b577b917dcafa7e6ea0" or len(ins)!=1279 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="211634fe59ac88b4624fa67b4c14302e537899dc385a3888f047ddf62341088e" or ind!=[0x5B4A40]:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=324 or sh(non)!="b26937b4176a7a4c69d4d525b632430beb9502a9b64976d24dcff8df7f8349e7" or sh(c._slice(b,*PHYS))!="fbc9447cd2f977850b1c4fef415b70e624928e73f16a6b7d0e48357c0924a986":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="07fab3c55df1797a5ef03782777071cc011fcf56d358e6119f280f9bb6e57951" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="bbe14020fcb62572a2def29a0a3f3bdffb9c27f48ac18746715fc0cbf94df12a":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,NANOPB,FIRST)
 if len(calls)!=218 or sum(y in starts for x,y in calls)!=4 or c._pair_digest(calls)!="923eb1080fe28665c9904e012c14d400ef83bf0198e841aaafb55ab40ae08b54" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(165,3,4,2,40):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=18 or c._pair_digest(entries)!="521bfa074c04331f4567fc362b9f25aaf82afeb8be5b579caad52f787a353db1" or strict:raise c.AuditError("raw ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=10 or c._pair_digest(stored)!="880e5252640de68192387453a13e4f4ed281641f16de6d06f0a39494d92114c6":raise c.AuditError("stored entry closure changed")
 if interior!=INTERIOR:raise c.AuditError("interior collision closure changed")
 table=struct.unpack_from('<13I',b,DISPATCH_TABLE-c.BASE)
 if set(table)!={0}|{a|1 for a in HANDLERS} or sum(v==0 for v in table)!=3:raise c.AuditError("dispatch table changed")
 if sh(c._slice(b,0x5B49C0,0x5B49D2))!="dd7b8c2701a3e23824f1df8c62fe22ed10745df5ce2fe851fce300cc5d19eba1" or sh(c._slice(b,0x5B4A38,0x5B4A42))!="b0d5de91521206147657c200223fcf8adb706831d69d5bedaea7450d3c4f3f10" or struct.unpack_from('<I',b,0x5B5404-c.BASE)[0]!=DISPATCH_TABLE:raise c.AuditError("indirect dispatch bound changed")
 pairs=sorted((cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell))
 if len(pairs)!=33 or c._pair_digest(pairs)!="aa7b5f3a0b8b65dba8062e778ff311b680126525439ca6c4e956b7a5f5a23902":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("conversate_pb_msg_handler" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\conversate\conversate_pb_msg_handler.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":15,"ghidra_discovered_functions":5,"restored_functions":10,"path_anchored_functions":5,"body_bytes":3440,"physical_bytes":3764,"noncode_bytes":324,"reachable_instructions":1279,"direct_body_calls":218,"internal_direct_body_calls":4,"external_direct_body_calls":214,"indirect_body_calls":1,"bounded_handler_table_entries":10,"direct_bl_entry_sites":18,"stored_function_entry_pointers":10,"raw_instruction_word_interior_collisions":2,"strict_interior_ingress":0},"provider_boundary":{"easylogger_calls":165,"iar_dlib_calls":3,"lvgl_calls":4,"nanopb_calls":2,"first_party_calls":40,"cmsis_freertos_calls":0,"freertos_kernel_calls":0,"historical_pb_msg_handler_commit":None,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
