#!/usr/bin/env python3
"""Register the source-owned queued runtime-context publisher."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_context_publish_42dca2.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000
SS=1752;SH="4915885eb4543890c828197dde035f13c0d987e11e9e19394391f4b9ed35d245";FN="open_cfw_bootloader_runtime_context_publish_42dca2";A=0x42DCA2;Z=0x42DD14;BH="200d91da3673bb39591b488795b73a7de75ffcba3f22e666af257ddd45a08f5d";UH="7203593c94d7fdf2b2075062728e5a981eaa73d282e3d7e06984b35aa55309bc";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"]
RS=((0x2A,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x38,"open_cfw_bootloader_queue_send_4168a2",0x4168A2),(0x5A,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x68,"open_cfw_bootloader_runtime_transfer_41623a",0x41623A))
def sha(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def main()->int:
 source=S.read_bytes();boot=B.read_bytes()
 if (len(source),sha(source))!=(SS,SH):raise SystemExit("context-publish source changed")
 if sha(boot[A-BASE:Z-BASE])!=BH:raise SystemExit("context-publish body changed")
 record={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room queued runtime-context publication and event notification","evidence":"docs/research/g2-bootloader-context-publish-42dca2-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in RS];pins={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};entry={"function":FN,"runtime_address":A,"source":record,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":pins,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":pins,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}}
 overlay=json.loads(O.read_text());overlay["in_place_leaves"]=sorted([x for x in overlay["in_place_leaves"] if x.get("function")!=FN]+[entry],key=lambda x:int(x["runtime_address"]));tmp=O.with_name(f".{O.name}.tmp");tmp.write_text(json.dumps(overlay,indent=2)+"\n");tmp.replace(O)
 with C.open(newline="") as f:reader=csv.DictReader(f,delimiter="\t");fields=list(reader.fieldnames or ());rows=list(reader)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("context-publish census changed")
 row.update({"kind":"source_function","name":"runtime_context_publish_42dca2","disposition":"source_owned_production","provider":"clean-room runtime-context publisher","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"});out=io.StringIO(newline="");writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);C.write_text(out.getvalue());print("registered runtime-context publisher");return 0
if __name__=="__main__":raise SystemExit(main())
