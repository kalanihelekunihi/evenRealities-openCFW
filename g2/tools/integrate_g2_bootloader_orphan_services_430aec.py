#!/usr/bin/env python3
"""Register two complete unreferenced linked bootloader services."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";CENSUS=ROOT/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_orphan_services_430aec.c"
SOURCE_SHA="692d609185272bb9ebc79d4342951766d02ac713f2bd8a727465e87ee5625dff";BASE=0x410000
ITEMS=(("open_cfw_bootloader_mode_four_wrapper_430aec",0x430AEC,0x430B0C,"8b4d130ac1735011011fd8a65ded46b1c5892049315798e9c477e1745d031fb7","a9e49da54bb521ea38ca1a1260604be4c4dfa6a7a6d7287ff5bb6b1f7848e6a4",[{"offset":8,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_mode_provider_430a60","symbol_type":"STT_NOTYPE","target_address":0x430A60}]),("open_cfw_bootloader_zero_table_431e38",0x431E38,0x431E70,"8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67","8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67",[]))
FLAGS=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
 source=SOURCE.read_bytes();boot=BOOT.read_bytes()
 if (len(source),sha(source))!=(2653,SOURCE_SHA):raise SystemExit("orphan source changed")
 record={"path":SOURCE.relative_to(ROOT).as_posix(),"size":len(source),"sha256":SOURCE_SHA,"license":"MIT","origin":"clean-room linked services without authenticated ingress","evidence":"docs/research/g2-bootloader-orphan-services-430aec-source-closure.md"};entries=[]
 for fn,s,e,h,u,rel in ITEMS:
  if sha(boot[s-BASE:e-BASE])!=h:raise SystemExit(f"body changed: {fn}")
  pins={"size":e-s,"sha256":h,"unrelocated_sha256":u};entries.append({"function":fn,"runtime_address":s,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FLAGS},"strict_relocation_contract":True,"expected":pins,"stock":{"size":e-s,"sha256":h},"relocations":rel,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":e-s,"sha256":h},"relocations":rel}}})
 overlay=json.loads(OVERLAY.read_text());names={x[0] for x in ITEMS};overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function") not in names]+entries,key=lambda x:int(x["runtime_address"]));tmp=OVERLAY.with_name(f".{OVERLAY.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(OVERLAY)
 with CENSUS.open(newline="") as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or ());rows=list(r)
 by={int(x["start"],16):x for x in rows}
 for fn,s,e,*_ in ITEMS:
  row=by.get(s)
  if row is None or int(row["end"],16)!=e:raise SystemExit(f"census changed: {fn}")
  row.update({"kind":"source_function","name":fn.removeprefix("open_cfw_bootloader_"),"disposition":"source_owned_production","provider":"clean-room complete linked service","license_status":"MIT","evidence":"exact dual-toolchain and Apollo-main body; no authenticated boot ingress"})
 out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);CENSUS.write_text(out.getvalue());print("registered two complete unreferenced linked services");return 0
if __name__=="__main__":raise SystemExit(main())
