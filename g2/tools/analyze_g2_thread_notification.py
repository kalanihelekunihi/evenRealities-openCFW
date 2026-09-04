#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for thread_notification.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-thread-notification-function-map.tsv";CL=ROOT/"tools/manifests/g2-thread-notification-closure.tsv";PM=ROOT/"tools/manifests/g2-thread-notification-provider-map.tsv"
PINS={FM:"7ba2927a61e1571ecbefcb47f3a3bf1e867ff1a2e22eb6328a3083724c019937",CL:"728c0e5b8a7d3936955db61126dfacb460135b8f6eccad67159e9bfd0eec7672",PM:"23cf26d8c720f864e58a8ce5c7e2494513808643e69e0657134510ba1d1190a9"}
F=((0x48E154,0x48E1CC),(0x48E1CC,0x48E1CE),(0x48E1CE,0x48E1F6),(0x48E1F6,0x48E1FE),(0x48E1FE,0x48E208),(0x48E208,0x48E212),(0x48E212,0x48E242),(0x48E242,0x48E25E),(0x48E25E,0x48E2B8),(0x48E2B8,0x48E34E),(0x48E34E,0x48E3E2),(0x48E3E2,0x48E42E));PHYS=(0x48E154,0x48E484);POOLS=((0x48E42E,0x48E484),)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x4490E2,0x4491FE,0x449238,0x4492C2,0x449376,0x449A32,0x449B3C,0x449BEC};FIRST={0x474D16,0x4972C2,0x49739E,0x497960,0x4C9B86,0x4C9BE2,0x4C9C3C,0x4D6A5C,0x4D6BA8,0x5FA0A4};STORED=[(0x48E44C,0x48E154),(0x794117,0x48E212)]
SOURCE=ROOT/"components/apollo_main/core_overlay/thread_notification.c";HEADER=ROOT/"components/apollo_main/core_overlay/thread_notification.h";OVERLAY=ROOT/"components/apollo_main/core_overlay/overlay.json";REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json"
PRODUCTION=("open_cfw_thread_notification_entry","open_cfw_thread_notification_init_hook","open_cfw_thread_notification_queue_init","open_cfw_thread_notification_whitelist_init","open_cfw_thread_notification_state_enter","open_cfw_thread_notification_state_ready","open_cfw_thread_notification_create","open_cfw_thread_notification_destroy","open_cfw_thread_notification_drain_queue","open_cfw_thread_notification_event_handler","open_cfw_thread_notification_exit","open_cfw_thread_notification_send_event")
def sh(x):return hashlib.sha256(x).hexdigest()
def production():
 source=SOURCE.read_bytes();header=HEADER.read_bytes()
 if (len(source),sh(source))!=(12275,"08b632f63bcc1fd356555a24616c274854e9e5e2767d01f6a78638f1ee40b6dc") or (len(header),sh(header))!=(1445,"39f27f59503b656ed93ceac2bab493728d5e48574b831d56c4e49017ac1df690"):raise c.AuditError("production notification source changed")
 config=json.loads(OVERLAY.read_text());rel={x.get("function"):x for x in config["relocated_leaves"] if x.get("function") in PRODUCTION};inp={x.get("function"):x for x in config["in_place_leaves"] if x.get("function") in PRODUCTION}
 if set(rel)!=(set(PRODUCTION)-{"open_cfw_thread_notification_init_hook"}) or set(inp)!={"open_cfw_thread_notification_init_hook"}:raise c.AuditError("production notification leaf inventory changed")
 if any(x.get("profiles")!=["apple-clang","linux-clang"] or x.get("strict_relocation_contract") is not True or x.get("source",{}).get("path")!="components/apollo_main/core_overlay/thread_notification.c" or x["source"].get("size")!=12275 or x["source"].get("sha256")!="08b632f63bcc1fd356555a24616c274854e9e5e2767d01f6a78638f1ee40b6dc" or x.get("expected",{}).get("alignment")!=4 or x.get("toolchain_profiles",{}).get("linux-clang",{}).get("expected",{}).get("alignment")!=4 for x in rel.values()):raise c.AuditError("production notification relocation contract changed")
 init=inp["open_cfw_thread_notification_init_hook"]
 if init.get("runtime_address")!=0x48E1CC or init.get("allow_halfword_placement") is not True or init.get("expected")!={"size":2,"sha256":"c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"} or init.get("stock")!=init.get("expected"):raise c.AuditError("production notification init hook changed")
 apple=sum(x["expected"]["size"] for x in rel.values())+2;linux=sum(x["toolchain_profiles"]["linux-clang"]["expected"]["size"] for x in rel.values())+2;ar=sum(len(x["relocations"]) for x in rel.values());lr=sum(len(x["toolchain_profiles"]["linux-clang"]["relocations"]) for x in rel.values())
 if (apple,linux,ar,lr)!=(400,400,31,31):raise c.AuditError("production notification compiled closure changed")
 patches=[x for x in config["patch_sites"] if x.get("name","").startswith("replace_thread_notification_")];patched={a for a,_ in F}-{0x48E1CC}
 if len(patches)!=11 or {x.get("runtime_address") for x in patches}!=patched or any(x.get("profiles")!=["apple-clang","linux-clang"] or x.get("branch")!="b_w" for x in patches):raise c.AuditError("production notification route changed")
 report=json.loads(REPORT.read_text());built={x.get("extraction",{}).get("function"):x for x in report["relocated_leaves"] if x.get("extraction",{}).get("function") in rel};built_in={x.get("extraction",{}).get("function"):x for x in report["in_place_leaves"] if x.get("extraction",{}).get("function") in inp}
 if set(built)!=set(rel) or set(built_in)!=set(inp) or any(built[n]["extraction"].get("sha256")!=rel[n]["expected"]["sha256"] or built[n]["placement"].get("offset")!=rel[n]["expected"]["offset"] for n in rel) or built_in["open_cfw_thread_notification_init_hook"]["extraction"].get("sha256")!=init["expected"]["sha256"]:raise c.AuditError("built notification route changed")
 validate_apollo_main_artifacts(ROOT,c.AuditError,"notification thread")
 return {"production_routed":True,"source_functions":12,"compiled_text_bytes":{"apple-clang":apple,"linux-clang":linux},"in_place_source_bytes":2,"strict_relocations":{"apple-clang":ar,"linux-clang":lr},"stock_replaced_bytes":730,"retained_diagnostic_pool_bytes":86,"software_functional_gap":False,"hardware_validation":"blocked by unavailable physical evidence","hardware_operations":[]}
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cms["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=12:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=3 or len(body)!=730 or sh(body)!="d33d3f94736d47aee0e41ba8c0eaac4c947d13668407b81f7c3b202cc04d5ab0" or code!=body or len(ins)!=282 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="db259b3c68c58df665955e9d56a59766a88dc0ece5585709065697ddb86b6806" or ind:raise c.AuditError("instruction closure changed")
 pool=b"".join(c._slice(b,*bounds) for bounds in POOLS)
 if sh(c._slice(b,*PHYS))!="24b82e6135ae9148a9ae3c4ddfb62fd5dbfc56d1f8614b1b985efee790a767b9" or len(pool)!=86 or sh(pool)!="62a32f0bc3bc9e64571afe79730216236574da30990cfdedc44506773b799a59":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x48E0A8,PHYS[0]))!="3364aa7bd737a4436eee41df6a102a6c60a774ceb30350e2e2d29dda5fd9df2b" or sh(c._slice(b,PHYS[1],0x48E494))!="f27e504dc20d0f5c8f1e8e78135ae9082765054660b5ac65e7994f50caab1df9":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,FIRST)
 if len(calls)!=58 or sum(y in starts for _,y in calls)!=8 or c._pair_digest(calls)!="48a93f8327a189caf960fe8d2ae03785484a244efde16b8b14ab232f50a3ece9" or set(ext)!=set().union(*providers):raise c.AuditError("call topology changed")
 if tuple(sum(ext[x] for x in group) for group in providers)!=(30,8,12):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=9 or c._pair_digest(entries)!="e5602bc285f8c623c1909b60323cc16ea467bd6af9e314ed347f8feece4c2ed0" or strict:raise c.AuditError("BL entry topology changed")
 stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];target=v&~1
  if v&1 and target in starts:stored.append((c.BASE+off,target))
 if stored!=STORED or c._pair_digest(stored)!="81c35ccb0bf7d083c22334292af3dbcd7abe1d3743fa766a0356425d3aa5a556":raise c.AuditError("stored entry topology changed")
 if t.literal_references(b,0x48E438)!=[0x48E19E,0x48E2D4,0x48E31A,0x48E37A,0x48E3B2,0x48E3FA]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure plus production-route validation","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":12,"ghidra_discovered_functions":9,"restored_functions":3,"path_anchored_functions":3,"body_bytes":730,"physical_bytes":816,"outer_pool_bytes":86,"direct_body_calls":58,"internal_direct_body_calls":8,"external_direct_body_calls":50,"indirect_body_calls":0,"direct_bl_entry_sites":9,"stored_entry_pointers":2},"provider_boundary":{"easylogger_calls":30,"cmsis_freertos_calls":8,"first_party_calls":12,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","cmsis_wrappers":["osThreadNew","osThreadTerminate","osThreadFlagsSet","osThreadFlagsWait","osDelay","osMessageQueueNew","osMessageQueueGet","osMessageQueueDelete"],"new_version_discriminator":False},"production":production()}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
