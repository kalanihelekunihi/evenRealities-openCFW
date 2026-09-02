#!/usr/bin/env python3
"""Register the source-owned hardware register-profile restoration service."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_hw_register_profile_restore_42f2fa.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42F2FA;Z=0x42F38E
SS=2930;SH="ced66ffb51c4ebc148e5ed32314117f89b84b4ba41d939b86412c1c0833ec35f";FN="open_cfw_bootloader_hw_register_profile_restore_42f2fa";BH="b1b11b9cae5d09e8bd59aae4099ed288cbd5d1e55980dbdda910c89282b7af40";UH="fbc38be724a162f01ab84627f97fa0843a969e4fedd792f00e1f2783fd13314a";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"];RS=((0x3C,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0x84,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0x8C,"open_cfw_bootloader_mode_finalize_41cde0",0x41CDE0))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("register-profile restore source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("register-profile restore stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room hardware register-profile restoration and finalization","evidence":"docs/research/g2-bootloader-hw-register-profile-restore-42f2fa-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("register-profile restore census changed")
 row.update({"kind":"source_function","name":"hw_register_profile_restore_42f2fa","disposition":"source_owned_production","provider":"clean-room hardware register-profile restoration","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered register-profile restore service");return 0
if __name__=="__main__":raise SystemExit(main())
