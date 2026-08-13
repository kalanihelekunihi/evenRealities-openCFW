#!/usr/bin/env python3
"""Fail-closed object/provider audit for ui_onboarding_main_page.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-onboarding-main-page-function-map.tsv";CL=ROOT/"tools/manifests/g2-onboarding-main-page-closure.tsv";PM=ROOT/"tools/manifests/g2-onboarding-main-page-provider-map.tsv"
PINS={FM:"c5597ddfa2ea23358b3a7e4765f3a9cd74b270c91678bf8b903581bb3f05888a",CL:"9e2021f6b6d481137a7d8a21450f993342accbae90fdead8a013977f7c394817",PM:"c127a53722b411e70c543f276f5c08dafceac777d46dd7135db55150766053f6"}
PHYS=(0x4A8560,0x4AAB90)
RESTORED={0x4A865E,0x4A8668,0x4A86C6,0x4A8720,0x4A872C,0x4A874C,0x4A87D0,0x4A8D96,0x4A8DB6,0x4A8E6C,0x4A908C,0x4A90CC,0x4A9118,0x4A915C,0x4A9C0C}
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4,0x44B728};CMSIS={0x4490CC,0x4497B6,0x44981C};MPALAND={0x4B4728};PROTOBUF={0x4A7D4E}
LVGL={0x43DED4,0x43DFA4,0x43E0E0,0x43F09A,0x43F0E0,0x43F142,0x43F506,0x43F66C,0x43F6D6,0x43FC70,0x43FCE0,0x43FD9E,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x441488,0x44BDEA,0x44DCA2,0x44E498,0x44EA04,0x4503D6,0x450408,0x4506CE,0x498680,0x49942E,0x50EBE2,0x50EC94,0x50ECEE}
FIRST={0x45A568,0x45FFFE,0x460084,0x464BB2,0x464C36,0x4AB004,0x509CA2,0x509DFA,0x509E14,0x509F52,0x509F7A,0x509F86,0x509F8E,0x50A094,0x50A4EE,0x50A9C2,0x50AAFC,0x50AC5C,0x50D578,0x50D894,0x50DAB8,0x50DB34,0x50F810,0x50FC86,0x50FE0E,0x50FE56}
PATH_CELLS={0x4A91D8:[0x4A88D0,0x4A898E],0x4A9C00:[0x4A9220,0x4A92E8,0x4A9A8E,0x4A9B60],0x4AAB64:[0x4A9F36,0x4A9FF8,0x4AAA16]}
STORED=[(0x4A91E4,0x4A87D1),(0x4A91EC,0x4A87D9),(0x4A938C,0x4A8827),(0x4A9394,0x4A8669),(0x4A9398,0x4A8671),(0x4A939C,0x4A8A25),(0x4A93A0,0x4A865F),(0x4A93A8,0x4A8611),(0x4AA040,0x4A86C7),(0x4AA0BC,0x4A8721),(0x4AA0C4,0x4A872D),(0x4AA1F8,0x4A86D3),(0x4AA1FC,0x4A874D),(0x4AA204,0x4A908D),(0x4AA208,0x4A9119),(0x4AA268,0x4A90CD),(0x4AA26C,0x4A915D)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());kernel=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text());deps={x["family"]:x for x in json.loads((ROOT/"tools/manifests/g2-third-party-dependency-closure.json").read_text())["dependencies"]}
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or cmsis["upstreams"]["cmsis_5"]["selected_commit"]!="2b7495b8535bdcb306dac29b9ded4cfb679d7e5c" or kernel["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c":raise c.AuditError("RTOS/logger provenance changed")
 if deps["mpaland-printf"]["selected_source_commit"]!="d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e" or deps["nanopb"]["selected_source_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("formatter/protobuf provenance changed")
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
 if len(F)!=52 or {a for a,z in F}&RESTORED!=RESTORED or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError("inventory changed")
 starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b'';uncovered=[]
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256']:raise c.AuditError("body changed")
  uncovered+=c._uncovered((a,z),ii);inter.update(range(a+2,z,2));ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if uncovered!=[(0x4AA64C,0x4AA654)] or c._slice(b,0x4AA64C,0x4AA654).hex()!="6c4d0720e44c0720":raise c.AuditError("inline literal changed")
 if len(body)!=9234 or sh(body)!="177b95a515f8b9bfcce1bd536ab84c0255b284a1f040ce0c285eb6407ee7881a" or len(ins)!=3632 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="4e0e4558dbfa7507973cd0edd03863d547674744314af140a79adf82ac6ba9fb" or ind:raise c.AuditError("instruction closure changed")
 non=b'';p=PHYS[0]
 for a,z in F:
  if a>p:non+=c._slice(b,p,a)
  p=z
 if p<PHYS[1]:non+=c._slice(b,p,PHYS[1])
 if len(non)!=542 or sh(non)!="e53d24e41e39cbe43b4b03d3c453faf244d8d3a1635f2aa6ffac071b870e38d7" or sh(c._slice(b,*PHYS))!="1e56738ca6a3dec41cba99d0f72098f840d69ec44a8c2f8256cc5206720c767a":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,0x4A8550,PHYS[0]))!="d520a5c0cac485e45ce776a970fef5145145d0fd7822b10d43f9efea8d0e84f9" or sh(c._slice(b,PHYS[1],0x4AABA0))!="a72126e8f4720ad87584ac0a4717ce72454ba764a3b628cbf29e9a48354fd812":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(LVGL,EASY,CMSIS,IAR,MPALAND,PROTOBUF,FIRST)
 if len(calls)!=533 or sum(y in starts for x,y in calls)!=80 or c._pair_digest(calls)!="d78e59c7e5388e942370fd00c113dcd39091e97c387209d775e0dcc597f33719" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(264,45,23,17,4,1,99):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=118 or c._pair_digest(entries)!="4e3bcb855ca31789eb7c28838f093d756117315139e5812943af3e4c990e8993" or strict:raise c.AuditError("entry closure changed")
 enc=starts|{a|1 for a in starts};stored=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3) if struct.unpack_from('<I',b,o)[0] in enc]
 if stored!=STORED:raise c.AuditError("stored callbacks changed")
 if cstring(b,0x6EAAB0)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c":raise c.AuditError("path changed")
 for cell,refs in PATH_CELLS.items():
  if t.literal_references(b,cell)!=refs:raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("ui_onboarding_main_page" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\onboarding\ui_onboarding_main_page.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":52,"ghidra_discovered_functions":37,"restored_functions":15,"path_anchored_functions":7,"body_bytes":9234,"physical_bytes":9776,"noncode_bytes":542,"reachable_instructions":3632,"direct_body_calls":533,"internal_direct_body_calls":80,"external_direct_body_calls":453,"indirect_body_calls":0,"direct_bl_entry_sites":118,"stored_entry_pointers":17,"strict_interior_ingress":0},"behavior":{"stored_callback_entries":17,"page_construction_and_layout":True,"sibling_news_and_stock_page_transitions":True,"mutex_serialized_page_state":True,"onboarding_protobuf_integration":True},"provider_boundary":{"lvgl_calls":264,"easylogger_calls":45,"cmsis_freertos_calls":23,"iar_dlib_calls":17,"mpaland_printf_calls":4,"closed_onboarding_protobuf_calls":1,"first_party_calls":99,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","mpaland_commit":"d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
