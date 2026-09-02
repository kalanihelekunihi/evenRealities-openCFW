#!/usr/bin/env python3
"""Register source-owned runtime context, control, and terminal wrappers."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_control_wrappers_42dd68.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SOURCE_SIZE=3213;SOURCE_SHA="4da52af0ccc849f743d3f2e298a33c6769b1776239faf84dbcb7d8ad2e32cd56"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_runtime_context_wrapper_42dd68",0x42DD68,0x42DD70,"86bf8be3cfef3a107d8691b1fb960ba63cc40d3ef6eb8ed906638e24001e1a84","c27d4a49b161be022ccdfdf92c47a4912090c2316b87ed52a61f20660f5f4dc3",((2,"open_cfw_bootloader_runtime_context_get_42d88a",0x42D88A),)),
 ("open_cfw_bootloader_control_one_wrapper_42dd9a",0x42DD9A,0x42DDA4,"0ca6febf5ed7d28e9c024276b7e6b431494e53a1432d1cdf6993024364aa64de","2cb70dab61786bb8a0ca4c358e1158432893275d7ed07c6004ce79c7b711b906",((4,"open_cfw_bootloader_control_one_42e3e0",0x42E3E0),)),
 ("open_cfw_bootloader_control_two_wrapper_42dda4",0x42DDA4,0x42DDAE,"a02566589b66a631938391fbfa5c8e950eac62d5a45e037fbf7b94de93e95cb2","2cb70dab61786bb8a0ca4c358e1158432893275d7ed07c6004ce79c7b711b906",((4,"open_cfw_bootloader_control_two_42e412",0x42E412),)),
 ("open_cfw_bootloader_control_bits_dispatch_42e1c4",0x42E1C4,0x42E1DA,"8aa6ac1511e5e2da57a358e821a85859d7ffb97ef6e2b326f56f0eb276bae818","192c434907f6c4eb54fbe5790cd26c5ef9279e3417fe6bb3b4f29c25f0f639a9",((8,"open_cfw_bootloader_control_fault_42de58",0x42DE58),(0x10,"open_cfw_bootloader_control_terminal_loop_provider_42e1da",0x42E1DA))),
 ("open_cfw_bootloader_control_terminal_loop_42e1da",0x42E1DA,0x42E1EC,"52e02a7a6d3c381ed3daa583fb765a14e5b7610f3e9ff1ad3b259da0ce762ca3","08fbcbd480f53dd4e0516ed99b0ee572d3f850af576459f1ce1c7e53771a3c47",((4,"open_cfw_bootloader_control_terminal_42e444",0x42E444),(0x0C,"open_cfw_bootloader_runtime_notify_416378",0x416378))),
)
def sha(value:bytes)->str:return hashlib.sha256(value).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("control-wrapper source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room runtime context, control, and terminal wrappers","evidence":"docs/research/g2-bootloader-control-wrappers-42dd68-source-closure.md"};entries=[]
 for function,start,end,body_sha,unreloc_sha,reloc_specs in ITEMS:
  if sha(boot[start-BASE:end-BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target} for offset,symbol,target in reloc_specs];pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":unreloc_sha};entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs}}})
 overlay=json.loads(OVERLAY.read_text());names={item[0] for item in ITEMS};overlay["in_place_leaves"]=sorted([item for item in overlay["in_place_leaves"] if item.get("function") not in names]+entries,key=lambda item:int(item["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by_start={int(row["start"],16):row for row in rows}
 for function,start,end,*_ in ITEMS:
  row=by_start.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room runtime control wrapper","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue());print("registered runtime control wrappers");return 0
if __name__=="__main__":raise SystemExit(main())
