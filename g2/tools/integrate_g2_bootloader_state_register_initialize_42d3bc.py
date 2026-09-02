#!/usr/bin/env python3
"""Register the source-owned state-transition register initializer."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_state_register_initialize_42d3bc.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42D3BC;Z=0x42D562
SS=6296;SH="06b62fbf0e0828aa0d87134a022115973a5fe5b3541ec81d499ef48d3149e706";FN="open_cfw_bootloader_state_register_initialize_42d3bc";BH="28b119628520d11368f8517e23ba59254c17bb974684a59ead1266312f71e0c6";UH="e9f07abd3d46704129114ec4e23d3a0702e9fab7d84c19b1b3376ea27e06af46";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"];RS=((0x7C,"open_cfw_bootloader_delay_us_41d1c0",0x41D1C0),(0xA6,"open_cfw_bootloader_delay_us_41d1c0",0x41D1C0))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("state-register initializer source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("state-register initializer stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room state-transition register initialization and restoration","evidence":"docs/research/g2-bootloader-state-register-initialize-42d3bc-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("state-register initializer census changed")
 row.update({"kind":"source_function","name":"state_register_initialize_42d3bc","disposition":"source_owned_production","provider":"clean-room state-transition register initialization and restoration","license_status":"MIT","evidence":"exact dual-toolchain body, sole caller, Apollo-main analogue, and portable register-transition model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered state-register initializer");return 0
if __name__=="__main__":raise SystemExit(main())
