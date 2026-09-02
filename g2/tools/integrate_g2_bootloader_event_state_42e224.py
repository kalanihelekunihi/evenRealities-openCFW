#!/usr/bin/env python3
"""Register source-owned retained event-state services."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_event_state_42e224.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SS=5139;SH="e825a0580bf65be09b19827e8fcb43297689347d58fdbe8b769889c1ddb99b6b";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(("open_cfw_bootloader_retained_state_probe_42e224",0x42E224,0x42E254,"cbb734736967e924c509fd7a235cc7be828b37a7f73ea981c52bd0f4438b4eec","46497ad8bd1d7e5ef5ee9c8605fcb19d93899052694d0315ab0341db032d744d",((0x1A,"open_cfw_bootloader_log_4176ce",0x4176CE),)),("open_cfw_bootloader_event_flags_init_42e254",0x42E254,0x42E276,"d5ddf3da1b0a6ad069d11bf5fa3f7cee7bb7b49da7f88f5f7fc41db45f3c8682","d09ea77084ebbcd63badf8f4cb17da34515b888b0461430076cef398e2014264",((0x06,"open_cfw_bootloader_event_flags_create_4164da",0x4164DA),(0x12,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8))),("open_cfw_bootloader_guard_context_init_42e39c",0x42E39C,0x42E3CA,"1b39880e3d47e3da3e72511ef04e72f33ed5dbf7bb4bdc1e678cc1ec8e3346e2","6618177ec909d6f2574ce8a75118a613d8c9d1a2790a698458f6b40a1ed48724",((0x02,"open_cfw_bootloader_runtime_prepare_416058",0x416058),(0x0E,"open_cfw_bootloader_runtime_dispatch_4160fe",0x4160FE),(0x1A,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8),(0x28,"open_cfw_bootloader_runtime_finalize_4160b0",0x4160B0))),("open_cfw_bootloader_control_one_wait_42e3e0",0x42E3E0,0x42E412,"2db659b64257eab40973463ed42d70b5bb519506294f949a56792e597ebae723","3908088fe1891671c347f922421e245639edd851ab3531ed42b17c05dc6917a8",((0x0E,"open_cfw_bootloader_event_wait_4162c4",0x4162C4),(0x2C,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_control_two_publish_42e412",0x42E412,0x42E444,"22dc8b8696ddc339b98a05705bbda6aa19bd401b7c9ee611bd51e4f42fe68cc9","e9ab8f7d865551e747a28b8032cbe2ddc27450afef8159d84aa5e7543ab92d98",((0x1C,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x2C,"open_cfw_bootloader_event_bits_set_41652e",0x41652E))))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=S.read_bytes();boot=B.read_bytes()
 if (len(source),sha(source))!=(SS,SH):raise SystemExit("event-state source changed")
 record={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room retained event-state probe, initialization, and control services","evidence":"docs/research/g2-bootloader-event-state-42e224-source-closure.md"};entries=[]
 for fn,a,z,h,u,rs in ITEMS:
  if sha(boot[a-BASE:z-BASE])!=h:raise SystemExit(f"body changed: {fn}")
  rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in rs];pins={"size":z-a,"sha256":h,"unrelocated_sha256":u};entries.append({"function":fn,"runtime_address":a,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr}}})
 overlay=json.loads(O.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="") as f:reader=csv.DictReader(f,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for fn,a,z,*_ in ITEMS:
  row=by.get(a)
  if row is None or int(row["end"],16)!=z:raise SystemExit(f"census changed: {fn}")
  row.update({"kind":"source_function","name":fn.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room retained event-state service","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);C.write_text(out.getvalue());print("registered retained event-state services");return 0
if __name__=="__main__":raise SystemExit(main())
