#!/usr/bin/env python3
"""Register the source-owned hardware clock-divider encoder."""
from __future__ import annotations
import csv, hashlib, io, json
from pathlib import Path
R=Path(__file__).resolve().parent.parent
O=R/"components/bootloader/core_overlay/overlay.json"
S=R/"components/bootloader/core_overlay/runtime_hw_clock_encode_42c26a.c"
B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BASE=0x410000; A=0x42C26A; Z=0x42C3E2
SS=5818; SH="3ecc609ac0bd37a2cc636df321644419b52d0cbc16939fc17133abf83fef7cf0"
FN="open_cfw_bootloader_hw_clock_encode_42c26a"
BH="23796b78366978bda2ee2db94e309c4f1cae4e92f5ffbc2072f75becca3ae9e8"
UH="1a25dd314239f7529ac9e4ea0d6dd690acda443e34cc35eb85fbb223baa349f5"
FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
RS=((0x12A,"open_cfw_bootloader_rounded_divider_42c222",0x42C222),(0x148,"open_cfw_bootloader_is_power_of_two_42c256",0x42C256),(0x15E,"open_cfw_bootloader_rounded_divider_42c222",0x42C222))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 s=S.read_bytes(); b=B.read_bytes()
 if(len(s),sha(s))!=(SS,SH):raise SystemExit("hardware-clock encoder source changed")
 if sha(b[A-BASE:Z-BASE])!=BH:raise SystemExit("hardware-clock encoder stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room hardware clock-divider search and register encoder","evidence":"docs/research/g2-bootloader-hw-clock-encode-42c26a-source-closure.md"}
 rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS]
 pins={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH}
 entry={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}}
 overlay=json.loads(O.read_text());overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"]if x.get("function")!=FN]+[entry],key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("hardware-clock census changed")
 row.update({"kind":"source_function","name":"hw_clock_encode_42c26a","disposition":"source_owned_production","provider":"clean-room hardware clock encoder","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"})
 out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered hardware clock encoder");return 0
if __name__=="__main__":raise SystemExit(main())
