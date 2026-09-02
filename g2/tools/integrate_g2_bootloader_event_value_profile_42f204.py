#!/usr/bin/env python3
"""Register the source-owned event-value hardware-profile publisher."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_event_value_profile_42f204.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42F204;Z=0x42F2FA
SS=5357;SH="fbe0f21e8279794d32b8b91958740ac9dc1753fc458ce3370c93a7cce19628bf";FN="open_cfw_bootloader_event_value_provider_42f204";BH="501f73cf98677984aeedc3b9d60df3775a99c7e68520f23d6bd11c8b0e342317";UH="afc00b5ad826855d562f2c1f82f67b728ea5144b92754578cc319e35fcb10b0d";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
RS=((0x0C,"open_cfw_bootloader_mode_finalize_41cde0",0x41CDE0),(0x64,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0xD0,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0xD6,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0),(0xEE,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("event-value profile source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("event-value profile stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room event-value hardware-profile publisher","evidence":"docs/research/g2-bootloader-event-value-profile-42f204-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("event-value profile census changed")
 row.update({"kind":"source_function","name":"event_value_profile_42f204","disposition":"source_owned_production","provider":"clean-room event-value hardware-profile publisher","license_status":"MIT","evidence":"exact dual-toolchain body, Apollo-main analogue, and portable register model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered event-value hardware-profile publisher");return 0
if __name__=="__main__":raise SystemExit(main())
