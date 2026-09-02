#!/usr/bin/env python3
"""Register the source-owned hardware-state decoder and classifier."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_hw_state_decode_42b6b8.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42B6B8;Z=0x42B9BA
SS=10192;SH="67170ef4a1621e6a6bb564cb963fb981774fca0b906b14263bdeb755cc746ddb";FN="open_cfw_bootloader_hw_state_decode_42b6b8";BH="74f4304f6e3aa59022a29eb5e5f5479c77072b33355825b7c9409897001bb9d1";UH=BH;FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("hardware-state decoder source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("hardware-state decoder stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room hardware-state nibble composition and dual-output classification","evidence":"docs/research/g2-bootloader-hw-state-decode-42b6b8-source-closure.md"};p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":[],"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":[]}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("hardware-state decoder census changed")
 row.update({"kind":"source_function","name":"hw_state_decode_42b6b8","disposition":"source_owned_production","provider":"clean-room hardware-state nibble composition and dual-output classification","license_status":"MIT","evidence":"exact relocation-free dual-toolchain body, sole caller, Apollo-main analogue, literals, and exhaustive portable classifier model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered hardware-state decoder");return 0
if __name__=="__main__":raise SystemExit(main())
