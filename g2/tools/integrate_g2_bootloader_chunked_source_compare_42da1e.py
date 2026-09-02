#!/usr/bin/env python3
"""Register the source-owned 4 KiB chunked source-comparison service."""
from __future__ import annotations
import csv,hashlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parent.parent;O=R/"components/bootloader/core_overlay/overlay.json";S=R/"components/bootloader/core_overlay/runtime_chunked_source_compare_42da1e.c";B=R/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";C=R/"tools/manifests/g2-bootloader-post-mspi-frontier.tsv";BASE=0x410000;A=0x42DA1E;Z=0x42DAD0
SS=2864;SH="41239ad9ae8bf2e12df17f7377ad09c38b0f70dde534f5f135838ce85852a724";FN="open_cfw_bootloader_chunked_source_compare_42da1e";BH="4addc6bfb9023df944da168fed7deb268b2de24817dd19865719e37f4131216b";UH="bb1588dad52910df21eed899b2baeca89620ce541261e8e511fecd04f539e471";FL=["-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never"];RS=((0x1A,"open_cfw_bootloader_compare_prepare_41e348",0x41E348),(0x42,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x7C,"open_cfw_bootloader_memory_compare_415758",0x415758),(0xA6,"open_cfw_bootloader_log_4176ce",0x4176CE))
def h(x):return hashlib.sha256(x).hexdigest()
def main():
 s=S.read_bytes();b=B.read_bytes()
 if(len(s),h(s))!=(SS,SH):raise SystemExit("chunked source-comparison source changed")
 if h(b[A-BASE:Z-BASE])!=BH:raise SystemExit("chunked source-comparison stock changed")
 rec={"path":S.relative_to(R).as_posix(),"size":SS,"sha256":SH,"license":"MIT","origin":"clean-room bounded 4 KiB source-reader comparison service","evidence":"docs/research/g2-bootloader-chunked-source-compare-42da1e-source-closure.md"};rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in RS];p={"size":Z-A,"sha256":BH,"unrelocated_sha256":UH};e={"function":FN,"runtime_address":A,"source":rec,"toolchain":{"target":"arm-none-eabi","reviewed_version_prefix":"Apple clang version 21.0.0","flags":FL},"strict_relocation_contract":True,"expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr,"allow_discarded_alloc_sections":True,"toolchain_profiles":{"linux-clang":{"reviewed_version_prefix":"Homebrew clang version 22.1.8","expected":p,"stock":{"size":Z-A,"sha256":BH},"relocations":rr}}};o=json.loads(O.read_text());o["in_place_leaves"]=sorted([x for x in o["in_place_leaves"]if x.get("function")!=FN]+[e],key=lambda x:int(x["runtime_address"]));t=O.with_name(f".{O.name}.tmp");t.write_text(json.dumps(o,indent=2)+"\n");t.replace(O)
 with C.open(newline="")as f:r=csv.DictReader(f,delimiter="\t");fields=list(r.fieldnames or());rows=list(r)
 row=next((x for x in rows if int(x["start"],16)==A),None)
 if row is None or int(row["end"],16)!=Z:raise SystemExit("chunked source-comparison census changed")
 row.update({"kind":"source_function","name":"chunked_source_compare_42da1e","disposition":"source_owned_production","provider":"clean-room 4 KiB source-reader comparison","license_status":"MIT","evidence":"exact dual-toolchain body with portable behavioral model"});out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows);C.write_text(out.getvalue());print("registered chunked source-comparison service");return 0
if __name__=="__main__":raise SystemExit(main())
