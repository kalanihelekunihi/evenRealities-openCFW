#!/usr/bin/env python3
"""Bind native-compared Apollo page editing state helpers."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_editing_44d510.c"
OUT=G2/"build/c-firmware/20261015/main-page-editing-44d510"
BASE=G2/"build/c-firmware/20261015/main-page-unlink-44d3b2/apollo-main-page-unlink-44d3b2.o"
ORACLE=HERE/"verify_main_page_editing_44d510_oracle_20261015.py"
PROVIDERS={"audio_uart_page_context_find_44d77a","audio_uart_lv_obj_event_451670",
           "audio_uart_display_size_changed","audio_uart_lvgl_log"}
DEFINITIONS={"audio_uart_page_set_editing_44d510","audio_uart_page_active_object_44d58c",
             "audio_uart_page_get_editing_44d5a4"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm",flag,str(path)],text=True).splitlines()}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_editing_44d510.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    defined=symbols(BASE,"--defined-only")
    if not PROVIDERS<=defined or DEFINITIONS & defined:
        raise RuntimeError("page editing provider/definition contract changed")
    linked=OUT/"apollo-main-page-editing-44d510.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before!=after or not DEFINITIONS<=symbols(linked,"--defined-only"):
        raise RuntimeError("page editing link contract changed")
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_EDITING_ORACLE" or \
            oracle["cases"]!=432 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("page editing oracle changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_EDITING_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "existing_providers":sorted(PROVIDERS),"definitions":sorted(DEFINITIONS),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":[],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Three adjacent page-editing bodies are native-compared in 432 controlled cases.",
                       "Logger internals, full LVGL object semantics, image layout and hardware remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))


if __name__=="__main__":
    main()
