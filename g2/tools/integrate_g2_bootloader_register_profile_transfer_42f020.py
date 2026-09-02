#!/usr/bin/env python3
"""Register the source-owned hardware register-profile capture/apply service."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_register_profile_transfer_42f020.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42F020;Z=0x42F14E
SS=5748;SH="998df67af4570a50d2682a7b8186ba31b57a70725ca1723b08248c0fc75e18fc";FN="open_cfw_bootloader_register_profile_transfer_42f020";BH="2e6cca806f60cc19024673c46f635245eaea0c8e7aff23580b1a8cf15e487a73";UH="7019743d54c61b4d148d591856d90a4c23d482770fc7938db8b4b374ef53278c";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"];RS=((0x3E,"open_cfw_bootloader_mode_query_41bf84",0x41BF84),(0x4C,"open_cfw_bootloader_mode_enable_route_4222f0",0x4222F0),(0x11E,"open_cfw_bootloader_clock_config_422364",0x422364),(0x124,"open_cfw_bootloader_delay_status_41c17a",0x41C17A))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("register-profile transfer source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("register-profile transfer stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room validated hardware register-profile capture/apply service","evidence":"docs/research/g2-bootloader-register-profile-transfer-42f020-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("register-profile transfer census changed")
 row.update({"kind":"source_function","name":"register_profile_transfer_42f020","disposition":"source_owned_production","provider":"clean-room validated hardware register-profile capture/apply service","license_status":"MIT","evidence":"exact dual-toolchain body, near-identical Apollo-main analogue, and portable profile model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered register-profile transfer");return 0
if __name__=="__main__":raise SystemExit(main())
