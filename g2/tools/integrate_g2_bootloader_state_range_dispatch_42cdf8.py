#!/usr/bin/env python3
"""Register the G2 state-adjust, range-update, and event-dispatch services."""
from __future__ import annotations
import csv, hashlib, io, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json"
SOURCE=ROOT/"components/bootloader/core_overlay/runtime_state_range_dispatch_42cdf8.c"
BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BOOT_BASE=0x00410000
SOURCE_SIZE=12765
SOURCE_SHA="ccd29db6d561a2c57c49b11ede15576ee0de2dc633715b49785ff805cd28a095"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin",
       "-ffunction-sections","-fdata-sections","-fno-unwind-tables",
       "-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror",
       "-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_state_adjust_42cdf8",0x0042CDF8,0x0042CEA4,
  "38a50cc07d40a0b1d447b195a21d977b7484f4d3151feead6e34dee388b59991",
  "38a50cc07d40a0b1d447b195a21d977b7484f4d3151feead6e34dee388b59991",()),
 ("open_cfw_bootloader_state_range_update_42ced8",0x0042CED8,0x0042CFE0,
  "5cf1d6490be8e99cbc802900d5021f53a44fd49ab34fae01f67cc4308c11b5a0",
  "7079a7b2881536c84b873867f4fcfe177d2164b023b3c536df80113790472752",
  ((0xA0,"open_cfw_bootloader_state_apply_42cea4",0x0042CEA4,"STT_NOTYPE"),
   (0xC8,"open_cfw_bootloader_state_apply_42cea4",0x0042CEA4,"STT_NOTYPE"),
   (0xEC,"open_cfw_bootloader_state_apply_42cea4",0x0042CEA4,"STT_NOTYPE"))),
 ("open_cfw_bootloader_state_event_dispatch_42d562",0x0042D562,0x0042D5C2,
  "a060f2a726d07c0c67a1c00ada3aa671c805cfdab3a34e26239a7ebafc86eaa3",
  "158ed49963d8dad49a00049283c61ebe50419c678e920125a47ad1d4f0073123",
  ((0x2A,"open_cfw_bootloader_state_event_zero_42cfe0",0x0042CFE0,"STT_NOTYPE"),
   (0x3A,"open_cfw_bootloader_state_event_one_zero_42d3bc",0x0042D3BC,"STT_NOTYPE"),
   (0x44,"open_cfw_bootloader_state_event_one_value_42d104",0x0042D104,"STT_NOTYPE"),
   (0x4E,"open_cfw_bootloader_state_range_update_42ced8",0x0042CED8,"STT_FUNC"))),
)
def sha(payload:bytes)->str:return hashlib.sha256(payload).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("state/range source changed")
 entries=[]
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,
         "license":"MIT","origin":"clean-room state/range services",
         "evidence":"docs/research/g2-bootloader-state-range-dispatch-42cdf8-source-closure.md"}
 for function,start,end,body_sha,unreloc_sha,reloc_specs in ITEMS:
  if sha(boot[start-BOOT_BASE:end-BOOT_BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,
           "symbol_type":symbol_type,"target_address":target}
          for offset,symbol,target,symbol_type in reloc_specs]
  pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":unreloc_sha}
  entries.append({"function":function,"runtime_address":start,"source":record,
   "toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},
   "strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},
   "relocations":relocs,"allow_discarded_alloc_sections":True,
   "toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8",
    "expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs}}})
 overlay=json.loads(OVERLAY.read_text());names={item[0] for item in ITEMS}
 overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]))
 temp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");temp.write_text(json.dumps(overlay,indent=2)+"\n");temp.replace(OVERLAY)
 with CENSUS.open(newline="",encoding="utf-8") as stream:
  reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(row["start"],16):row for row in rows}
 for function,start,end,*_ in ITEMS:
  row=by.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census boundary changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),
              "disposition":"source_owned_production","provider":"clean-room state/range service",
              "license_status":"MIT","evidence":"exact dual-toolchain and Apollo-main body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n")
 writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue(),encoding="utf-8")
 print("registered state/range/dispatch services");return 0
if __name__=="__main__":raise SystemExit(main())
