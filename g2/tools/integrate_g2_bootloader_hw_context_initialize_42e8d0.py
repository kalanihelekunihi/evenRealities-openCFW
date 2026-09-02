#!/usr/bin/env python3
"""Register the source-owned hardware-context initializer."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_hw_context_initialize_42e8d0.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42E8D0;Z=0x42EA32
SS=5816;SH="89691e672633cd9590206a01475ebe2affd3b0c64ac886b6f606d8b3207b179b";FN="open_cfw_bootloader_hw_context_initialize_42e8d0";BH="21eb4fbe548c1f7c1c16bbf7bf31671f7cdbf125ee784a96893efdef723f6fd8";UH="b34fa81a3f580579a5260a539ef14f81e8b7bfdbbed0978e88dbba4c69e17c06";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"];RS=((0x94,"open_cfw_bootloader_config_read_421548",0x421548),(0xA4,"open_cfw_bootloader_config_read_421548",0x421548),(0xB6,"open_cfw_bootloader_config_read_421548",0x421548),(0x116,"open_cfw_bootloader_config_read_421548",0x421548),(0x126,"open_cfw_bootloader_config_read_421548",0x421548))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("hardware-context initializer source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("hardware-context initializer stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room hardware-context slot and calibration-profile initializer","evidence":"docs/research/g2-bootloader-hw-context-initialize-42e8d0-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("hardware-context initializer census changed")
 row.update({"kind":"source_function","name":"hw_context_initialize_42e8d0","disposition":"source_owned_production","provider":"clean-room hardware-context slot and calibration-profile initializer","license_status":"MIT","evidence":"exact dual-toolchain body, sole caller, Apollo-main analogue, and portable profile/default model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered hardware-context initializer");return 0
if __name__=="__main__":raise SystemExit(main())
