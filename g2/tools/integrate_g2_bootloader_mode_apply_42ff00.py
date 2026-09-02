#!/usr/bin/env python3
"""Register the source-owned mode router and aggregate-bitset service."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_mode_apply_42ff00.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42FF00;Z=0x42FFF2
SS=4417;SH="fe029db3a951fc9ff53e2c438560bd0df2c7716fcc238dc91fae355e56022f90";FN="open_cfw_bootloader_mode_apply_42ff00";BH="2bf23ab0e4988009a2692db968a818ffeb5f010919982b1235db1b85d8735ae6";UH="3f26b603da390864dd2be07c458566263a63400f78d428f98113b1540bc53d1d";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
RS=((0x3C,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x52,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x68,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x7E,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x84,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0xC4,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0xCE,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0xEA,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("mode-apply source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("mode-apply stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room mode routing and aggregate bitset service","evidence":"docs/research/g2-bootloader-mode-apply-42ff00-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("mode-apply census changed")
 row.update({"kind":"source_function","name":"mode_apply_42ff00","disposition":"source_owned_production","provider":"clean-room mode routing and aggregate bitset service","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered mode-apply service");return 0
if __name__=="__main__":raise SystemExit(main())
