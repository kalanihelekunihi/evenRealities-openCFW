#!/usr/bin/env python3
"""Fail-closed object/provider audit for teleprompt/teleprompt_ui.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-teleprompt-ui-function-map.tsv";CL=ROOT/"tools/manifests/g2-teleprompt-ui-closure.tsv";PM=ROOT/"tools/manifests/g2-teleprompt-ui-provider-map.tsv"
PINS={FM:"51baec8f3ca9fb0f02dc1764d38a084bddbc482c269f5541206142c0d75e3e4d",CL:"f9d9ec1cc401b554b329a4a8e0816925299a47b3c079a96eeea641cae7668607",PM:"c34ffd16e9246d145ab0dc4245a78082afff8b31aec7148518834d43b9fca60c"}
PHYS=(0x554170,0x5574B0);PATH_CELLS=(0x554D38,0x5558C8,0x556488,0x556EC0,0x557444)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4,0x44A43C}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F4C0,0x43F568,0x43F66C,0x43F6B8,0x43F6D6,0x43FDDA,0x44104C,0x441180,0x4411AA,0x44120E,0x44121C,0x44122A,0x441238,0x441246,0x441254,0x44127E,0x44129E,0x4412EC,0x44130C,0x44131C,0x44132A,0x441386,0x4413CE,0x44140E,0x44143E,0x44144C,0x44145A,0x44146A,0x441498,0x44D7B8,0x44D878,0x44DACA,0x44DCE2,0x44E368,0x44E3CA,0x44E498,0x44E4BC,0x44E75E,0x44EA04,0x450286,0x4503D6,0x450408,0x4506CE,0x451740,0x498668,0x498680,0x499416,0x49942E,0x49954C,0x499678,0x499716,0x499752,0x499790,0x4997F8}
FIRST={0x44A1EA,0x45A568,0x45FFFE,0x460084,0x464C36,0x46AE9C,0x47D8CE,0x48BA78,0x48BA92,0x48EB32,0x554080,0x5540BC,0x5540D6,0x5540F0,0x5540F8,0x554102,0x588968,0x588A56,0x588C16,0x589152,0x5891B6,0x58930A,0x58966C,0x5896B4,0x5896FC,0x5897E0,0x5897EE,0x589B68,0x589CB4,0x58A680,0x58A83E,0x58B1C0,0x58B370,0x58B83C,0x58B8F0,0x58B980,0x58BD70,0x58BD74,0x58BFB2,0x58C238,0x58C7A0,0x58C836,0x58C84E,0x58C874,0x58C882}
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 if json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":raise c.AuditError("EasyLogger changed")
 if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text():raise c.AuditError("LVGL changed")
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
 if len(F)!=55 or sum(r['source_path_anchor']=='yes' for r in rows)!=8:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();ind.sort()
 if uncovered or len(body)!=12228 or sh(body)!="598c93d329ceb582fc3827e629db5c15945b022004e947f932e683b1814ef49b" or len(ins)!=4607 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="3c16f8a4316268309f65a4c283c497ca37bbf1e1732af93e02604ef598489c36" or ind!=[0x5543A2]:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=892 or sh(non)!="5ca10cd2194baaf30876f70451817c72d30ee3526c97cb3a021806e18bcd60cf" or sh(c._slice(b,*PHYS))!="46f86382b9d576bcf19dbf8177ef8e94f7c526670f81da8dd275918c78dd5b72":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="dc969ece11cdc60cf574582616b8b90231773de687820595d1ed8810ea7bfc30" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="7b8d812120081bbf8437a0d71abeec3c4dafe7970453ad56a8ecd0172e01156d":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,LVGL,IAR,FIRST)
 if len(calls)!=772 or sum(y in starts for x,y in calls)!=48 or c._pair_digest(calls)!="c93c51704cfc0e5373794525b9e6a3ff1ef743e9c7234d023d3b921335e9667b" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(330,252,10,132):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=63 or c._pair_digest(entries)!="3c6b3b1edc5887d076232285eb5d3938fd85ba714531f6059154e1b791bf0831" or strict:raise c.AuditError("BL ingress changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts}
 stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 real=[(a,v) for a,v in interior if (v&~1) in ins];pseudo=[(a,v) for a,v in interior if (v&~1) not in ins]
 if len(stored)!=27 or c._pair_digest(stored)!="106406952b6d774763dee200ef3452e961c14eafa5ff6852f3b3260da87c1012":raise c.AuditError("stored entries changed")
 if len(real)!=5 or len({v&~1 for a,v in real})!=2 or c._pair_digest(real)!="f99419f9f93b47164dda20d623b418a286a9ac108033ea5667cb27e43d9890fb":raise c.AuditError("interior callbacks changed")
 if len(pseudo)!=6 or c._pair_digest(pseudo)!="55eed7e8f0a62c19e737f8e3fbb823e578823b3503dc434d3baf71da5ba8f96f":raise c.AuditError("pseudo pointers changed")
 if cstring(b,0x6FD97C)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_ui.c":raise c.AuditError("path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=67 or c._pair_digest(pairs)!="fbf3ac0594bb04ff8b70423a3be92ae61274d45389a1f83bacceea5279ce2121":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("teleprompt_ui" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\teleprompt\teleprompt_ui.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":55,"ghidra_discovered_functions":17,"restored_functions":38,"path_anchored_functions":8,"body_bytes":12228,"physical_bytes":13120,"noncode_bytes":892,"reachable_instructions":4607,"direct_body_calls":772,"internal_direct_body_calls":48,"external_direct_body_calls":724,"indirect_body_calls":1,"direct_bl_entry_sites":63,"stored_function_entry_pointers":27,"stored_interior_callback_pointers":5,"stored_interior_callback_targets":2,"unaligned_word_pseudo_pointers":6,"strict_interior_bl_ingress":0},"behavior":{"mode_event_callback_dispatch":True,"teleprompt_screen_construction":True,"text_resource_rendering":True,"scroll_and_presentation_control":True,"configuration_and_file_state":True},"provider_boundary":{"easylogger_calls":330,"lvgl_calls":252,"iar_dlib_calls":10,"first_party_calls":132,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
