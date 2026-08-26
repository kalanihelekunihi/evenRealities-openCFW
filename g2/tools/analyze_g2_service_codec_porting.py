#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for service_codec_porting.c."""
import csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-service-codec-porting-function-map.tsv";CL=ROOT/"tools/manifests/g2-service-codec-porting-closure.tsv";PM=ROOT/"tools/manifests/g2-service-codec-porting-provider-map.tsv"
SOURCE=ROOT/"components/apollo_main/core_overlay/service_codec_porting.c";OVERLAY=ROOT/"components/apollo_main/core_overlay/overlay.json";BUILD_REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json";PACKAGE=ROOT/"build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin";FLASH_PLAN=ROOT/"build/source/flash-plan.json"
PINS={FM:"337862aacdaa492a409533d35cd3e0febbacd71efa315dfb79bbbe224adeff63",CL:"f2bfbbe9495901e6c1c38bedf6806420076348d44b295dc66623bbe80d0e6ff0",PM:"d5d00d196ab80981a3ce83c25e59ef3f7d59d46d82cb5d89356a84f6f5677081"}
F=((0x58FB52,0x58FC0C),(0x58FC0C,0x58FCA8));PHYS=(0x58FB52,0x58FCF0);POOL=(0x58FCA8,0x58FCF0);EASY={0x43CE9E,0x43D0CE,0x43D574};RING={0x598160};UART={0x55E5BC,0x55E630,0x55E8F0}
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());ring=json.loads((ROOT/"third_party/ring-buffer/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or ring["upstream"]["selected_commit"]!="190e30bebcec22d7311fd941179d70b4f439c441" or ring["selection"]["compatible_floor_commit"]!="cda00e1efb815bad5100757f0d10d117f633ced6":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=2:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=2 or len(body)!=342 or sh(body)!="7f6f4ef925199c29fde103206f6df39a4c02eb627765b2a3a856be3886847208" or code!=body or len(ins)!=141 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="ce83b160ac6abc49117a7b04d9bfe1af85435ff32546e86142f691f068265bca" or ind:raise c.AuditError("instruction closure changed")
 if sh(c._slice(b,*PHYS))!="10446a3c12344e7c02b1db8fe77c8d28435274bab0f5b6158c641db553b71ef8" or sh(c._slice(b,*POOL))!="96a643a249fff315b45a6534c7daaf0ac4f7a8e1f74285da45f14bbee62276e3":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x58FB38,PHYS[0]))!="2137e21e3e62c7e89959b6b89d7d1252dcb386f11311af11e77b568b6c08a760" or sh(c._slice(b,PHYS[1],0x58FD18))!="232e226bd1ece2ee0d8a14abc3461651743ef4c987b46406fc2995154ed59a29":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls);providers=(EASY,RING,UART)
 if len(calls)!=24 or c._pair_digest(calls)!="39d11d6cd9242d5bb1bf97f90fcadee709c54f9e399cf057b90a45a9ff05ce3e" or set(ext)!=set().union(*providers):raise c.AuditError("call topology changed")
 if tuple(sum(ext[x] for x in group) for group in providers)!=(20,1,3):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=7 or c._pair_digest(entries)!="e74341a2a1df4093d4dc9d71d67c6ee1a97b5d724f79b8e2ab5d40b3f54099b9" or strict:raise c.AuditError("BL entry topology changed")
 if t.literal_references(b,0x58FCC8)!=[0x58FB8C,0x58FBD6,0x58FC28,0x58FC72]:raise c.AuditError("path references changed")
 source_bytes=SOURCE.read_bytes()
 if (len(source_bytes),sh(source_bytes))!=(2633,"4ec2915a3bb15efd29e3c116116a3e3aaa306132953c5da3d5aac60e07e7de77"):raise c.AuditError("codec UART production source changed")
 source_text=source_bytes.decode("utf-8")
 for token in ("OPEN_CFW_CODEC_RING_INIT(OPEN_CFW_CODEC_RING", "OPEN_CFW_CODEC_RX_BUFFER, 64u", "OPEN_CFW_CODEC_UART_SET_RX_CALLBACK(3u", "OPEN_CFW_CODEC_UART_RESUME(3u)", "OPEN_CFW_CODEC_UART_SUSPEND(3u)"):
  if token not in source_text:raise c.AuditError("codec UART source policy changed")
 overlay=json.loads(OVERLAY.read_text());leaves=[x for x in overlay["relocated_leaves"] if x.get("source",{}).get("path")=="components/apollo_main/core_overlay/service_codec_porting.c"];patches=[x for x in overlay["patch_sites"] if x.get("target_function") in ("open_cfw_codec_uart_init","open_cfw_codec_uart_close")]
 expected_leaves=(
  ("open_cfw_codec_uart_init",{"alignment":4,"offset":299752,"sha256":"3605c2eaab426c4bbbd93ef42c7501fa6f67b72c49e6abed35e59080580e6361","size":86,"unrelocated_sha256":"3d740b4322ffc06de05e4aae19a51746dc582eb4301a611457ba257681a0c41b"},[(32,"open_cfw_codec_ring_init",0x598160),(46,"open_cfw_codec_uart_set_rx_callback",0x55E8F0),(64,"open_cfw_codec_uart_resume",0x55E5BC)]),
  ("open_cfw_codec_uart_close",{"alignment":4,"offset":299840,"sha256":"7ab968a2dedb91b09a9bafe3c4e0fc426524ad5d8e8f1622ff9f10218f21cc0d","size":40,"unrelocated_sha256":"a02bca80ff038e831bf70a6675e623e214a7c91758fbd77f019add55b348d7c0"},[(22,"open_cfw_codec_uart_suspend",0x55E630)]))
 for leaf,(name,pins,relocs) in zip(leaves,expected_leaves):
  if leaf.get("function")!=name or leaf.get("expected")!=pins or [(r["offset"],r["symbol"],r["target_address"]) for r in leaf.get("relocations",[])]!=relocs or any(r.get("type")!="R_ARM_THM_CALL" for r in leaf.get("relocations",[])):raise c.AuditError("codec UART relocated-leaf contract changed")
 for patch,(name,address,size,digest) in zip(patches,(("open_cfw_codec_uart_init",F[0][0],186,"a674dd367f19cd6dd65fcb5ee3a4ead12ae281b35c23978419a30a2fd12223d3"),("open_cfw_codec_uart_close",F[1][0],156,"3bad5828dd218631ebf8665d8809e3fc85aaaac36d696d6d6713ca270e316a57"))):
  if patch.get("target_function")!=name or patch.get("runtime_address")!=address or patch.get("expected_size")!=size or patch.get("expected_sha256")!=digest or patch.get("branch")!="b_w":raise c.AuditError("codec UART guarded redirect contract changed")
 build=json.loads(BUILD_REPORT.read_text());built=[x for x in build["relocated_leaves"] if x.get("source",{}).get("path")=="components/apollo_main/core_overlay/service_codec_porting.c"]
 if (build["overlay"]["size"],build["overlay"]["sha256"],build["component"]["size"],build["component"]["sha256"])!=(332148,"588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d",3855544,"df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc"):raise c.AuditError("codec UART production build pins changed")
 if [(x["extraction"]["function"],x["extraction"]["size"],x["extraction"]["alignment"],x["extraction"]["relocation_count"],x["placement"]["padding_before"]) for x in built]!=[("open_cfw_codec_uart_init",86,4,3,0),("open_cfw_codec_uart_close",40,4,1,2)]:raise c.AuditError("codec UART compiled report changed")
 manifest=json.loads(MANIFEST.read_text());main=manifest["component_overrides"]["apollo_main"]
 if (main["provider"]["size"],main["provider"]["sha256"],manifest["package"]["expected_size"],manifest["package"]["expected_sha256"])!=(3855544,"df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",4634038,"3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731"):raise c.AuditError("codec UART manifest/package pins changed")
 regions=[item for item in main["regions"] if item["name"].startswith("service_codec_porting")]
 if len(regions)!=8 or [item["size"] for item in regions]!=[166,186,156,72,15878,86,2,40] or [item["address_status"] for item in regions]!=["official_blob","generated_source_entry_replacement","generated_source_entry_replacement","official_blob","official_blob","source_compiled","generated_alignment","source_compiled"]:raise c.AuditError("codec UART manifest ownership changed")
 package_bytes=PACKAGE.read_bytes()
 if (len(package_bytes),sh(package_bytes))!=(4634038,manifest["package"]["expected_sha256"]):raise c.AuditError("codec UART package artifact changed")
 plan_bytes=FLASH_PLAN.read_bytes();plan=json.loads(plan_bytes)
 if (len(plan_bytes),sh(plan_bytes),plan.get("package_sha256"),tuple(len(plan[key]) for key in ("flash_regions","unresolved_flash_regions","container_only_regions","protected_regions")))!=(3108201,"e91992690cb5766623f0b95b0928d3113ea9c0deac6d12275d55db6f12741297","3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731",(4482,2,5,6)):raise c.AuditError("codec UART flash plan changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":2,"ghidra_discovered_functions":2,"path_anchored_functions":2,"body_bytes":342,"physical_bytes":414,"outer_pool_bytes":72,"direct_body_calls":24,"internal_direct_body_calls":0,"external_direct_body_calls":24,"indirect_body_calls":0,"direct_bl_entry_sites":7,"stored_entry_pointers":0},"provider_boundary":{"easylogger_calls":20,"ring_buffer_calls":1,"first_party_uart_calls":3,"ring_buffer_commit_interval":["cda00e1efb815bad5100757f0d10d117f633ced6","190e30bebcec22d7311fd941179d70b4f439c441"],"new_version_discriminator":False},"production":{"production_routed":True,"compiled_text_bytes":126,"alignment_bytes":2,"strict_relocations":4,"replaced_stock_body_bytes":342,"retained_official_pool_bytes":72,"hardware_validation":"blocked by unavailable authorized responsive G2 pair and live GX8002B UART3 evidence"}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
