#!/usr/bin/env python3
"""Register source-owned hardware-register, interrupt, NVIC, and SCB helpers."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_register_helpers_42c034.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SOURCE_SIZE=7511;SOURCE_SHA="c27b18bf5dbf3ae160ce50463e3677c88e074a0bb718819898ce205ec3c7e5c0"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_hw_status_route_42c034",0x42C034,0x42C076,"4748ace7dc077c4c00e8b22fb267ba5d64a0d28286c6b2d30868907e5ffa2005"),
 ("open_cfw_bootloader_hw_error_classify_42c076",0x42C076,0x42C0B2,"ccdc2830f8d713ac41be3ffae702c125009eed11fc8b89d5f430e8c3a794af19"),
 ("open_cfw_bootloader_hw_interrupt_enable_42c63a",0x42C63A,0x42C672,"4bb8cd7875f57a46da8764a7c89f6058ce9f5aac52f707e5c86dc7a66c20d775"),
 ("open_cfw_bootloader_hw_interrupt_status_get_42c672",0x42C672,0x42C6B6,"12a9d08495567647cb0d8416dfb736ee532845317b856b2b86e26b485510d347"),
 ("open_cfw_bootloader_hw_interrupt_clear_42c6b6",0x42C6B6,0x42C6E4,"4a307af7da21ad92dbface1def9fb21fe550c8452a2c1a6b01755fdd0d7e2d4a"),
 ("open_cfw_bootloader_nvic_enable_bit_430240",0x430240,0x43025C,"5f76b9bde6a1e386ed0ecb96e419aab2895f1cd30353dfac8bd7ef39b6fbd6c0"),
 ("open_cfw_bootloader_scb_priority_nibble_43025c",0x43025C,0x430280,"ecf2bd6399d01eec88b38fd549bb5c511b6e5c06de2741cd54904269245e4f55"),
 ("open_cfw_bootloader_nvic_enable_bit_430470",0x430470,0x43048E,"c71013637b644e67341b8f624db6831e06033c5a5323c421ef13a9f970883113"),
)
def sha(value:bytes)->str:return hashlib.sha256(value).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("register-helper source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room hardware-register, interrupt, NVIC, and SCB helpers","evidence":"docs/research/g2-bootloader-register-helpers-42c034-source-closure.md"};entries=[]
 for function,start,end,body_sha in ITEMS:
  if sha(boot[start-BASE:end-BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":body_sha};entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":[],"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":[]}}})
 overlay=json.loads(OVERLAY.read_text());names={item[0] for item in ITEMS};overlay["in_place_leaves"]=sorted([item for item in overlay["in_place_leaves"] if item.get("function") not in names]+entries,key=lambda item:int(item["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by_start={int(row["start"],16):row for row in rows}
 for function,start,end,*_ in ITEMS:
  row=by_start.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room register and interrupt helper","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue());print("registered hardware-register and interrupt helpers");return 0
if __name__=="__main__":raise SystemExit(main())
