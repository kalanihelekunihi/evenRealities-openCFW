#!/usr/bin/env python3
"""Register the source-owned stored-entry hardware-state composer."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_hw_state_compose_42bdf0.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42BDF0;Z=0x42BF4E
SS=5512;SH="7dc2091d350c71e142096fcf3b7f7c87f3b3bdd1df0be5d79f1f6bfb49288759";FN="open_cfw_bootloader_hw_state_compose_42bdf0";BH="6abb107b7aebe13eaff37f34185f8865b71f27c756f8214d3646efa4f2304c1c";UH="b58f55d554bf0421fd534e60ce347afec006da6d395801821ed11dbe26ff5f41";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"];RS=((0x3A,"open_cfw_bootloader_config_read_421548",0x421548),(0x96,"open_cfw_bootloader_config_read_421548",0x421548),(0xB8,"open_cfw_bootloader_config_read_421548",0x421548),(0x154,"open_cfw_bootloader_hw_state_commit_41cc04",0x41CC04))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("hardware-state composer source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("hardware-state composer stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room stored-entry hardware-state reader and packed-field composer","evidence":"docs/research/g2-bootloader-hw-state-compose-42bdf0-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("hardware-state composer census changed")
 row.update({"kind":"source_function","name":"hw_state_compose_42bdf0","disposition":"source_owned_production","provider":"clean-room stored-entry hardware-state reader and packed-field composer","license_status":"MIT","evidence":"exact dual-toolchain body, stored ingress, Apollo-main analogue, and portable packed-field model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered hardware-state composer");return 0
if __name__=="__main__":raise SystemExit(main())
