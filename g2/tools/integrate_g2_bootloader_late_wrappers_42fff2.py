#!/usr/bin/env python3
"""Register late runtime wrappers and correct the 0x430B10 function extent."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_late_wrappers_42fff2.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SOURCE_SIZE=5761;SOURCE_SHA="fae82be6e3f01f260574240ffc4ad3892b3369f5e874319c5808d505cf458c5f"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_mode_one_apply_42fff2",0x42FFF2,0x42FFFE,"75fb4f494d3b0844cdd83c4a29b56a600221b0c11cabe5a37da80055611739e5","5130a565487bf859f315758ff01bab0b9ba664d8c202f946fb7321f79f836b02",((0x06,"open_cfw_bootloader_mode_apply_42ff00",0x42FF00),)),
 ("open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC,0x4303DE,"c6f1ae52eca3aa5ea02a327560090a3b77b3603d70b8ef1db09ebf422b2495d1","20761cc03c65d94830c9f9ed045b754fed6db00929476daf9300f4e53475ede8",((0x10,"open_cfw_bootloader_boolean_route_41d9aa",0x41D9AA),)),
 ("open_cfw_bootloader_validated_byte_copy_430a9c",0x430A9C,0x430AC4,"227e07edede8d13c9bee39f2e4745468bb8290b3ae67e63d7af1b4546fb28ceb","f4365efc56e758fc3ac038c09d3e68afb1dc4f47ad7354c8bf6e94d21c22c466",((0x0C,"open_cfw_bootloader_address_validate_430a60",0x430A60),(0x1A,"open_cfw_bootloader_byte_copy_41568c",0x41568C))),
 ("open_cfw_bootloader_validated_word_transfer_430ac4",0x430AC4,0x430AEC,"e868f672a76b215ca5f17a8cedca05ef0df0eddaac7a9b5e1dc024464a768512","b975f25f8af7dc30afb5984a14bb71e933b92d02dfba04cd233bd7202b7e43fe",((0x0C,"open_cfw_bootloader_address_validate_430a60",0x430A60),(0x1A,"open_cfw_bootloader_word_transfer_provider_430b10",0x430B10))),
 ("open_cfw_bootloader_word_transfer_critical_430b10",0x430B10,0x430B3C,"2c87f99aa6b925741f616a9d79ff9fc3ccb3435fd812d87072f2946425dc6f91","fe3259e33c8cbb4cc0f524ffe128e948b6e2ff3371ae87859719334722c6dac3",((0x12,"open_cfw_bootloader_critical_save_41b8ec",0x41B8EC),(0x20,"open_cfw_bootloader_alignment_dispatch_42e4f4",0x42E4F4))),
 ("open_cfw_bootloader_platform_services_init_43194c",0x43194C,0x43198A,"3d057acab6aa34a7443a18c5f1a7a63133a12944656603585df0f08982d41316","f20e6cf0468641fe0cccff820de74f1dfee0ce7a5197ccecc9d1dfc2e816d7d9",((0x02,"open_cfw_bootloader_platform_init_41733c",0x41733C),(0x0A,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x12,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x1A,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x22,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x2A,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x32,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x36,"open_cfw_bootloader_platform_finish_417392",0x417392))),
)
def sha(value:bytes)->str:return hashlib.sha256(value).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("late-wrapper source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room late mode, validation, transfer, and platform wrappers","evidence":"docs/research/g2-bootloader-late-wrappers-42fff2-source-closure.md"};entries=[]
 for function,start,end,body_sha,unreloc_sha,reloc_specs in ITEMS:
  if sha(boot[start-BASE:end-BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target} for offset,symbol,target in reloc_specs];pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":unreloc_sha};entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs}}})
 overlay=json.loads(OVERLAY.read_text());names={item[0] for item in ITEMS};overlay["in_place_leaves"]=sorted([item for item in overlay["in_place_leaves"] if item.get("function") not in names]+entries,key=lambda item:int(item["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by_start={int(row["start"],16):row for row in rows};extent=by_start.get(0x430B10);following=by_start.get(0x430B38)
 if extent is None or extent["end"]!="0x00430b38" or following is None or following["end"]!="0x0043194c":raise SystemExit("0x430B10 legacy census extent changed")
 extent.update({"end":"0x00430b3c","size":"44","sha256":"2c87f99aa6b925741f616a9d79ff9fc3ccb3435fd812d87072f2946425dc6f91"});following.update({"name":"post_mspi_gap_00430b3c","start":"0x00430b3c","size":"3600","sha256":"4785451528046431af8e88e5cbf5fd93014d327113022e519f59de1b3f601b21"})
 by_start={int(row["start"],16):row for row in rows}
 for function,start,end,*_ in ITEMS:
  row=by_start.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room late runtime wrapper","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue());print("registered late runtime wrappers and corrected 0x430B10 extent");return 0
if __name__=="__main__":raise SystemExit(main())
