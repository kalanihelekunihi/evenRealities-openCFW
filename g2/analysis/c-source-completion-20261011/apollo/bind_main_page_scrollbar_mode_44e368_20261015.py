#!/usr/bin/env python3
"""Bind native-compared LVGL scrollbar-mode setter."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_scrollbar_mode_44e368.c"
OUT=G2/"build/c-firmware/20261015/main-page-scrollbar-mode-44e368"
BASE=G2/"build/c-firmware/20261015/main-page-editing-44d510/apollo-main-page-editing-44d510.o"
ORACLE=HERE/"verify_main_page_scrollbar_mode_44e368_oracle_20261015.py"
PROVIDERS={"audio_uart_lv_obj_setup_layer_43e1fa","audio_uart_display_size_changed",
           "audio_uart_lvgl_log"}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm",flag,str(path)],text=True).splitlines()}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_scrollbar_mode_44e368.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    defined=symbols(BASE,"--defined-only")
    if not PROVIDERS<=defined or "audio_uart_page_44e368" in defined:
        raise RuntimeError("scrollbar-mode provider/definition contract changed")
    linked=OUT/"apollo-main-page-scrollbar-mode-44e368.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!={"audio_uart_page_44e368"} or after-before or \
            "audio_uart_page_44e368" not in symbols(linked,"--defined-only"):
        raise RuntimeError("scrollbar-mode link contract changed")
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_SCROLLBAR_MODE_ORACLE" or \
            oracle["cases"]!=70 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("scrollbar-mode oracle changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_SCROLLBAR_MODE_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "existing_providers":sorted(PROVIDERS),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(before-after),"imports_added":sorted(after-before),
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["70 controlled native/C scrollbar-mode cases; lower calls are controlled.",
                       "Logger internals, LVGL layer allocation, image layout and hardware remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))


if __name__=="__main__":main()
