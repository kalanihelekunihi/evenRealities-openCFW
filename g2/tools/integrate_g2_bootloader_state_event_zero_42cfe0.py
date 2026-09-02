#!/usr/bin/env python3
"""Register the source-owned sixteen-channel state/event classifier."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_state_event_zero_42cfe0.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42CFE0;Z=0x42D0F2
SS=3987;SH="90321ad1e5150a4ddbd1a321638ad92f20cc81cd330f75e8ad3377c0b3c0eadc";FN="open_cfw_bootloader_state_event_zero_42cfe0";BH="c03a0f379d7bbafb93e2c9074e4d754081699d39c63b4c2820765ffdab996624";UH="01821e038de30d1a7e3cf1f0cb4e6124781b6860f1931800f3e89fe167b00e6a";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"];RS=((0x22,"open_cfw_bootloader_state_probe_41f3f0",0x41F3F0),)
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("state-event classifier source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("state-event classifier stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room sixteen-channel state/event classifier","evidence":"docs/research/g2-bootloader-state-event-zero-42cfe0-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("state-event classifier census changed")
 row.update({"kind":"source_function","name":"state_event_zero_42cfe0","disposition":"source_owned_production","provider":"clean-room sixteen-channel state/event classifier","license_status":"MIT","evidence":"exact dual-toolchain body, near-identical Apollo-main analogue, and portable range model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered state-event classifier");return 0
if __name__=="__main__":raise SystemExit(main())
