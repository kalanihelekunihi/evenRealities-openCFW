#!/usr/bin/env python3
"""Register source-owned event wait, teardown, and event-bit wrappers."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_control_wrappers_42e2ea.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SOURCE_SIZE=2109;SOURCE_SHA="5f463bd5de40f968582e0198d1214125e63946ff5b128c8393eb2e4cf9ad0b0d"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_event_wait_one_wrapper_42e2ea",0x42E2EA,0x42E2F8,"755001d459d0d7af2b51fc148548078f44c848f2c6e735507029ffc337ba07f8","b2e9d3e4bd105ff8427fa2c89ebc03d29ea7c87a36cedac9f8299220f1d69b5e",0x08,"open_cfw_bootloader_event_wait_42e2a2",0x42E2A2),
 ("open_cfw_bootloader_guarded_context_teardown_42e3ca",0x42E3CA,0x42E3E0,"544c355918dcd5b5ceb47a9c31bda9a753885aaf41bcd3ed957ae58e587fcf4f","74b4af3f060bbe60742d2e17e3f0001316738895cf91dc614049567d3f3185f2",0x0C,"open_cfw_bootloader_guarded_action_416200",0x416200),
 ("open_cfw_bootloader_event_bit_set_42e444",0x42E444,0x42E458,"3099730c70327b1b039a6b0ea58e5a9b2a50f8eab76da2a4dac89a4fb4565c3c","fb42d9e8e3c1ce65bb07a5817d38fa5aac8cdf0cf983f39c72173f661e205013",0x0E,"open_cfw_bootloader_event_bits_set_41652e",0x41652E),
)
def sha(value:bytes)->str:return hashlib.sha256(value).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("event-control wrapper source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room event wait, guarded teardown, and event-bit wrappers","evidence":"docs/research/g2-bootloader-event-control-wrappers-42e2ea-source-closure.md"};entries=[]
 for function,start,end,body_sha,unreloc_sha,offset,symbol,target in ITEMS:
  if sha(boot[start-BASE:end-BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target}];pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":unreloc_sha};entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs}}})
 overlay=json.loads(OVERLAY.read_text());names={item[0] for item in ITEMS};overlay["in_place_leaves"]=sorted([item for item in overlay["in_place_leaves"] if item.get("function") not in names]+entries,key=lambda item:int(item["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by_start={int(row["start"],16):row for row in rows}
 for function,start,end,*_ in ITEMS:
  row=by_start.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room event-control wrapper","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue());print("registered event-control wrappers");return 0
if __name__=="__main__":raise SystemExit(main())
