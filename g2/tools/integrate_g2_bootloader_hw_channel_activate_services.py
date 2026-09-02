#!/usr/bin/env python3
"""Register G2 hardware channel configuration and activation services."""
from __future__ import annotations
import csv, hashlib, io, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json"
BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BOOT_BASE=0x00410000
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin",
       "-ffunction-sections","-fdata-sections","-fno-unwind-tables",
       "-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror",
       "-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_hw_channel_config_42eaf6",0x0042EAF6,0x0042EB74,
  "components/bootloader/core_overlay/runtime_hw_channel_config_42eaf6.c",2949,
  "139c7e866bc382b84b94271a24306d137fdf29dd56968fa05ecce758fc3d35a4",
  "59424a9cdea76c34a98142a28944d1d1700758cc2412e7d1903be4757e1d3c04"),
 ("open_cfw_bootloader_hw_handle_activate_42ed60",0x0042ED60,0x0042EDA0,
  "components/bootloader/core_overlay/runtime_hw_handle_activate_42ed60.c",1439,
  "b75cff5fc5dbf72ba19ac32eabd897a2ebfaa5aa2f1e9e165b1d9b5d0ba21ab5",
  "5603c205e322271c30b9c91be82538938549b50a35f8e6d1ad94de5d1bb7eb23"),
)
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 boot=BOOT.read_bytes();entries=[]
 for function,start,end,path,size,source_sha,body_sha in ITEMS:
  source=(ROOT/path).read_bytes()
  if (len(source),sha(source))!=(size,source_sha):raise SystemExit(f"source changed: {function}")
  if sha(boot[start-BOOT_BASE:end-BOOT_BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  record={"path":path,"size":size,"sha256":source_sha,"license":"MIT",
          "origin":"clean-room hardware channel/activation service",
          "evidence":"docs/research/g2-bootloader-hw-channel-activate-source-closure.md"}
  pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":body_sha}
  entries.append({"function":function,"runtime_address":start,"source":record,
   "toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},
   "strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},
   "relocations":[],"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{
    "reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,
    "stock":{"size":end-start,"sha256":body_sha},"relocations":[]}}})
 overlay=json.loads(OVERLAY.read_text());names={x[0] for x in ITEMS}
 overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]))
 temp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");temp.write_text(json.dumps(overlay,indent=2)+"\n");temp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:
  reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for function,start,end,*_ in ITEMS:
  row=by.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census boundary changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),
              "disposition":"source_owned_production","provider":"clean-room hardware channel/activation service",
              "license_status":"MIT","evidence":"exact dual-toolchain and Apollo-main body with portable register model"})
 out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);CENSUS.write_text(out.getvalue())
 print("registered hardware channel configuration and activation services");return 0
if __name__=="__main__":raise SystemExit(main())
