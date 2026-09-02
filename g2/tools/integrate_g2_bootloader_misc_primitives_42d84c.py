#!/usr/bin/env python3
"""Register source-owned post-MSPI mode, vector, CRC, and terminal primitives."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_misc_primitives_42d84c.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SOURCE_SIZE=4007;SOURCE_SHA="90d948a301d9d5ef34f8de6f9b0037f9a6abb7dc328868054520288e23b99deb"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(("open_cfw_bootloader_stream_mode_42d84c",0x42D84C,0x42D88A,"f477b0cb43f2f3074d2eeb48722f1045786679e4bc688fcf0440e842aeafa468"),("open_cfw_bootloader_runtime_context_get_42d88a",0x42D88A,0x42D890,"a38decb7c6c890f46354bc3a4b166bd89e4dac78108f0a6eb1e6123e61ad8087"),("open_cfw_bootloader_vector_handoff_42dc90",0x42DC90,0x42DCA2,"71c5efb5c61ed7560ffa777e2f1ae2a3c65f0cace89f79de6e95b57f64673d6d"),("open_cfw_bootloader_crc32_table_42e1ec",0x42E1EC,0x42E220,"b7d1a53f8d5f9e32fd1b27f48a14cf24bbfe5c7eb572950301fe0b32eff2f84a"),("open_cfw_bootloader_terminal_mode_42e514",0x42E514,0x42E534,"9c8ad2fd0e9722f5f6c902aee90dc63e6fbd7188827a02b16b6262421fa5107b"))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("misc primitive source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room mode/vector/CRC/terminal primitives","evidence":"docs/research/g2-bootloader-misc-primitives-42d84c-source-closure.md"};entries=[]
 for function,start,end,body_sha in ITEMS:
  if sha(boot[start-BASE:end-BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":body_sha};entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":[],"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":[]}}})
 overlay=json.loads(OVERLAY.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by={int(x["start"],16):x for x in rows}
 for function,start,end,*_ in ITEMS:
  row=by.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room mode/vector/CRC/terminal primitive","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);CENSUS.write_text(out.getvalue());print("registered miscellaneous post-MSPI primitives");return 0
if __name__=="__main__":raise SystemExit(main())
