#!/usr/bin/env python3
"""Register source-owned event runtime initialization, dispatch, and enqueue services."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_event_runtime_services_42e53c.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SS=5524;SH="9d427b3851f3680b514e5b9b02b9ed9e3cdb973b5aaf1a60dc8db4de2cdffc11";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(("open_cfw_bootloader_event_runtime_init_42e53c",0x42E53C,0x42E642,"8cbbeffaffa2a5c06366020712b77d72be670a18d7ff3c319da22d4cc5bd60e1","d86265af7b562c0a4f2b77135c615aaf8a4ad4befd4fe80b48fd39c1f3cb1517",((0x14,"open_cfw_bootloader_queue_create_416816",0x416816),(0x38,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x54,"open_cfw_bootloader_named_object_create_4163b2",0x4163B2),(0x78,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x8C,"open_cfw_bootloader_event_object_create_416610",0x416610),(0xB0,"open_cfw_bootloader_log_4176ce",0x4176CE),(0xC2,"open_cfw_bootloader_runtime_object_delete_416200",0x416200),(0xDA,"open_cfw_bootloader_runtime_task_create_4160fe",0x4160FE),(0xFE,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_event_callback_loop_42e644",0x42E644,0x42E686,"12cee7c0ef1b572aab563a611afef44f7a04b723797499083ab338c6dc34d413","955ecd8eea75b567485ae7c243dc4ebe3e191c28f0a7acf5a35ca9d5c427c037",((0x1A,"open_cfw_bootloader_queue_receive_416920",0x416920),(0x3C,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_event_callback_enqueue_42e686",0x42E686,0x42E6F2,"8d2dc54d9c093c0c8ee2ef3c2b390c2719cb6b22fde97ccc7845cf180c960ed3","ec7c3afdd0a93421ade6491970da330e86857830703e57e3005e46e1aff4133f",((0x28,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x42,"open_cfw_bootloader_queue_send_4168a2",0x4168A2),(0x64,"open_cfw_bootloader_log_4176ce",0x4176CE))))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=S.read_bytes();boot=B.read_bytes()
 if (len(source),sha(source))!=(SS,SH):raise SystemExit("event-runtime source changed")
 record={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room event runtime initialization, callback dispatch, and enqueue services","evidence":"docs/research/g2-bootloader-event-runtime-services-42e53c-source-closure.md"};entries=[]
 for fn,a,z,h,u,rs in ITEMS:
  if sha(boot[a-BASE:z-BASE])!=h:raise SystemExit(f"body changed: {fn}")
  rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in rs];pins={"size":z-a,"sha256":h,"unrelocated_sha256":u};entries.append({"function":fn,"runtime_address":a,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr}}})
 overlay=json.loads(O.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="") as f:reader=csv.DictReader(f,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for fn,a,z,*_ in ITEMS:
  row=by.get(a)
  if row is None or int(row["end"],16)!=z:raise SystemExit(f"census changed: {fn}")
  row.update({"kind":"source_function","name":fn.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room event runtime service","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);C.write_text(out.getvalue());print("registered event runtime services");return 0
if __name__=="__main__":raise SystemExit(main())
