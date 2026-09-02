#!/usr/bin/env python3
"""Register G2 hardware configuration and channel-enumeration services."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_config_enumerate_42ec0c.c"
BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BOOT_BASE=0x00410000
SOURCE_SIZE=16137;SOURCE_SHA="4bed46d7fc7a8008ef67b360d218d433a59e8df8a0a1e2d277b06899cd5b9cf6"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_hw_config_dispatch_42ec0c",0x42EC0C,0x42ED60,"b8b072619837474e9b6403d4097b20aedd8ce7f7ec8a458a1445c3574630fa83","b8b072619837474e9b6403d4097b20aedd8ce7f7ec8a458a1445c3574630fa83",()),
 ("open_cfw_bootloader_hw_channel_normalize_42ee00",0x42EE00,0x42EE6C,"8211026e1a7232d3cc7b527820d21a5bf55b843b9843e2db588c55777c909cb1","8211026e1a7232d3cc7b527820d21a5bf55b843b9843e2db588c55777c909cb1",()),
 ("open_cfw_bootloader_hw_channel_enumerate_42ee70",0x42EE70,0x42EFF4,"4051c15947e7cbab52ab6cc9a9a5993cddbd41ad9acf68b406fdee30066f5d9b","c69884c4fc9d791f76c2c7ef79eef74beafef2c7ae343162a99f7d1f9d91c655",(0x5A,0x160)),)
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("hardware config source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room hardware configuration/channel enumeration services","evidence":"docs/research/g2-bootloader-hw-config-enumerate-42ec0c-source-closure.md"};entries=[]
 for function,start,end,body_sha,unreloc_sha,offsets in ITEMS:
  if sha(boot[start-BOOT_BASE:end-BOOT_BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_hw_channel_normalize_42ee00","symbol_type":"STT_FUNC","target_address":0x42EE00} for offset in offsets]
  pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":unreloc_sha}
  entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs}}})
 overlay=json.loads(OVERLAY.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));temp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");temp.write_text(json.dumps(overlay,indent=2)+"\n");temp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for function,start,end,*_ in ITEMS:
  row=by.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census boundary changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room hardware configuration/channel service","license_status":"MIT","evidence":"exact dual-toolchain and Apollo-main body with portable register model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue())
 print("registered hardware configuration and channel enumeration services");return 0
if __name__=="__main__":raise SystemExit(main())
