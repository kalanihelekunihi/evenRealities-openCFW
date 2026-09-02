#!/usr/bin/env python3
"""Register the source-owned bounded hardware-configuration retry service."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_hw_config_retry_43048e.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x43048E;Z=0x430502
SS=2454;SH="800e836227e6f754f325ef05134f1ffe184d5dc0f7d5175d178b212cb6a2e745";FN="open_cfw_bootloader_hw_config_retry_43048e";BH="6ba3fb6ddde5fa56fd43fc1f7f717bcc7cf201df2ae6af1b86d20bdde8404dbb";UH="d38d571a4434f154b7f72b56d99123af55902ac5105c4202cc13087a0971b418"
FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
RS=((0x24,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x36,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x40,"open_cfw_bootloader_delay_us_41f9d8",0x41F9D8),(0x5E,"open_cfw_bootloader_hw_config_transaction_42c988",0x42C988))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("hardware-config retry source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("hardware-config retry stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room bounded hardware-configuration retry and callback setup","evidence":"docs/research/g2-bootloader-hw-config-retry-43048e-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("hardware-config retry census changed")
 row.update({"kind":"source_function","name":"hw_config_retry_43048e","disposition":"source_owned_production","provider":"clean-room bounded hardware-configuration retry","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered hardware-config retry service");return 0
if __name__=="__main__":raise SystemExit(main())
