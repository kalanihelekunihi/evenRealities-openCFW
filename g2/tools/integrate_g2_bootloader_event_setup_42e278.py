#!/usr/bin/env python3
"""Register source-owned event-runtime setup and callback dispatch wrappers."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_setup_42e278.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SOURCE_SIZE=2076;SOURCE_SHA="f1f061f6c312116e123b3579243a79516303e092eabf32ed5ab3a883328bb170"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_event_runtime_setup_42e278",0x42E278,0x42E284,"467af532a72d356addb9577ade72a626da8322be6ff7ed42015afb2f56b42741","4658dcdec39f0fc2e56a1cf1cff6e832accdd7f1553438b173a234bc9923629e",((0x02,"open_cfw_bootloader_event_runtime_init_42e53c",0x42E53C),(0x06,"open_cfw_bootloader_event_callback_dispatch_provider_42e284",0x42E284))),
 ("open_cfw_bootloader_event_callback_dispatch_42e284",0x42E284,0x42E2A2,"fd2c715cd5191d39eac7a7dee7b7a14d0a3f03f4caaca7fcae41bf32c8f72c67","7041c47adb8f1c02f7770e4d5d707bacfc44b02b77a5e5b053b40f2a711bf156",((0x02,"open_cfw_bootloader_runtime_value_4161c6",0x4161C6),(0x08,"open_cfw_bootloader_runtime_call_4161ce",0x4161CE),(0x12,"open_cfw_bootloader_runtime_value_4161c6",0x4161C6),(0x18,"open_cfw_bootloader_runtime_call_4161ce",0x4161CE))),
)
def sha(value:bytes)->str:return hashlib.sha256(value).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("event-setup source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room event-runtime setup and callback-dispatch wrappers","evidence":"docs/research/g2-bootloader-event-setup-42e278-source-closure.md"};entries=[]
 for function,start,end,body_sha,unreloc_sha,relocation_specs in ITEMS:
  if sha(boot[start-BASE:end-BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target} for offset,symbol,target in relocation_specs];pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":unreloc_sha};entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs}}})
 overlay=json.loads(OVERLAY.read_text());names={item[0] for item in ITEMS};overlay["in_place_leaves"]=sorted([item for item in overlay["in_place_leaves"] if item.get("function") not in names]+entries,key=lambda item:int(item["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by_start={int(row["start"],16):row for row in rows}
 for function,start,end,*_ in ITEMS:
  row=by_start.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room event-runtime setup wrapper","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue());print("registered event-runtime setup wrappers");return 0
if __name__=="__main__":raise SystemExit(main())
