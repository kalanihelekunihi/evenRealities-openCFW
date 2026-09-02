#!/usr/bin/env python3
"""Register source-owned command-queue initialization and control adapters."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_cmdq_adapters_42c3e2.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SOURCE_SIZE=3673;SOURCE_SHA="f921a48a361f0d474781128b9ea4fe4b15a83727db472cb1178f78d66b954ff2"
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
ITEMS=(
 ("open_cfw_bootloader_cmdq_adapter_init_42c3e2",0x42C3E2,0x42C420,"1aa65df1cc920ea6fc753560e93e4967b36d8f0d49b1c37f9dd0b26295f84f02","7cb32beffb23a70bd84b37e9535483c46443570121bdf064f548ece05a7117cc",0x2C,"open_cfw_bootloader_cmdq_init_427794",0x427794),
 ("open_cfw_bootloader_cmdq_adapter_enable_42c420",0x42C420,0x42C44E,"1714c962c633337cdcde5ef6b032ac0bb3f10324ac0320e57fa8120c368bd4d3","66be604a116d307934ea0c3368c4c62c93ede52c84f494f3e25e844907eb4d4b",0x28,"open_cfw_bootloader_cmdq_enable_427878",0x427878),
 ("open_cfw_bootloader_cmdq_adapter_disable_42c44e",0x42C44E,0x42C45A,"d967623a77aff3dfbddc473422f508342a52aae0fa9b3e79c0215f3b62434157","e701bdc5d633faefd76b340e85ef86e0099177411ae4c6a202515a211c684fc1",0x06,"open_cfw_bootloader_cmdq_disable_4278c8",0x4278C8),
)
def sha(value:bytes)->str:return hashlib.sha256(value).hexdigest()
def main()->int:
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(SOURCE_SIZE,SOURCE_SHA):raise SystemExit("command-queue adapter source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":SOURCE_SIZE,"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room command-queue initialization and control adapters","evidence":"docs/research/g2-bootloader-cmdq-adapters-42c3e2-source-closure.md"};entries=[]
 for function,start,end,body_sha,unreloc_sha,offset,symbol,target in ITEMS:
  if sha(boot[start-BASE:end-BASE])!=body_sha:raise SystemExit(f"body changed: {function}")
  relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target}];pins={"size":end-start,"sha256":body_sha,"unrelocated_sha256":unreloc_sha};entries.append({"function":function,"runtime_address":start,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":end-start,"sha256":body_sha},"relocations":relocs}}})
 overlay=json.loads(OVERLAY.read_text());names={item[0] for item in ITEMS};overlay["in_place_leaves"]=sorted([item for item in overlay["in_place_leaves"] if item.get("function") not in names]+entries,key=lambda item:int(item["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as stream:reader=csv.DictReader(stream,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 by_start={int(row["start"],16):row for row in rows}
 for function,start,end,*_ in ITEMS:
  row=by_start.get(start)
  if row is None or int(row["end"],16)!=end:raise SystemExit(f"census changed: {function}")
  row.update({"kind":"source_function","name":function.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room command-queue adapter","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue());print("registered command-queue adapters");return 0
if __name__=="__main__":raise SystemExit(main())
