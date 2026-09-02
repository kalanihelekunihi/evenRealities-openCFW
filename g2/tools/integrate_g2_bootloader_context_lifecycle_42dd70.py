#!/usr/bin/env python3
"""Register source-owned retained runtime-context lifecycle helpers."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_context_lifecycle_42dd70.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SS=3930;SH="e4b74c635f5f0e841b756900eb1d1ae9c20062a753b735a6fa6522725a2a766a";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(("open_cfw_bootloader_runtime_queue_context_init_42dd70",0x42DD70,0x42DD98,"b1a116c4a0b095a6b25414510fcd994e43043a3cb8048d6adecb0ccd4e62e9a7","73d3c112f75080f61acae6675511fc705a04b817e3c588408bd30042eaa5c47c",((0x0C,"open_cfw_bootloader_runtime_queue_create_416816",0x416816),(0x18,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8))),
("open_cfw_bootloader_runtime_action_context_init_42ddae",0x42DDAE,0x42DDDA,"380371eb1ff732482bbf5862d645eeb7e2198d5366513a326da54e1493fab666","d82b70ae5c6d7b9e075ac3ba24496e5eb54cb87365becdd9add92fc50bc8e574",((0x10,"open_cfw_bootloader_runtime_dispatch_4160fe",0x4160FE),(0x1C,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8))),
("open_cfw_bootloader_runtime_action_context_deinit_42ddda",0x42DDDA,0x42DDF2,"11df23f5964afb35c73937e9b03e8b010cce58ad1d840e5ea106b8b1abd1b6c1","dbd84048dbc1728d0fc7a7c13f4426b3bb37398349dc7bb813edbb70b9736448",((0x0E,"open_cfw_bootloader_runtime_action_416200",0x416200),)),
("open_cfw_bootloader_runtime_enable_sequence_42ddf2",0x42DDF2,0x42DE0E,"2e690fb77d2d549104eaeb32851f8dfc94e079fb872890a5258604be9be8782c","f5c0449de46d42f24c63c3f558dc9aa63ca0b7123ee43e08ba92dc47e209f6d4",((0x02,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x08,"open_cfw_bootloader_runtime_enable_41f8ba",0x41F8BA),(0x12,"open_cfw_bootloader_runtime_mode_set_41ba80",0x41BA80),(0x16,"open_cfw_bootloader_runtime_commit_41c990",0x41C990))))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=S.read_bytes();boot=B.read_bytes()
 if (len(source),sha(source))!=(SS,SH):raise SystemExit("context-lifecycle source changed")
 record={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room retained runtime-context lifecycle and sequencing helpers","evidence":"docs/research/g2-bootloader-context-lifecycle-42dd70-source-closure.md"};entries=[]
 for fn,a,z,h,u,rs in ITEMS:
  if sha(boot[a-BASE:z-BASE])!=h:raise SystemExit(f"body changed: {fn}")
  rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in rs];pins={"size":z-a,"sha256":h,"unrelocated_sha256":u};entries.append({"function":fn,"runtime_address":a,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":z-a,"sha256":h},"relocations":rr}}})
 overlay=json.loads(O.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="") as f:reader=csv.DictReader(f,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for fn,a,z,*_ in ITEMS:
  row=by.get(a)
  if row is None or int(row["end"],16)!=z:raise SystemExit(f"census changed: {fn}")
  row.update({"kind":"source_function","name":fn.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room runtime-context lifecycle helper","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);C.write_text(out.getvalue());print("registered runtime-context lifecycle helpers");return 0
if __name__=="__main__":raise SystemExit(main())
