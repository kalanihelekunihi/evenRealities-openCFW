#!/usr/bin/env python3
"""Bind native-compared Apollo LVGL object clean and lower gates."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_clean_44d878.c"
OUT=G2/"build/c-firmware/20261015/main-page-clean-44d878"
BASE=G2/"build/c-firmware/20261015/main-lv-first-live-child-44e164/apollo-main-lv-first-live-child-44e164.o"
ORACLE=HERE/"verify_main_page_clean_44d878_oracle_20261015.py"
PROVIDERS={"audio_uart_display_size_changed","audio_uart_lv_child_count_44ddea",
           "audio_uart_lv_first_live_child_44e164","audio_uart_lv_obj_event_451670",
           "audio_uart_lvgl_log"}
LOWER={"audio_uart_lv_child_delete_44df80","audio_uart_lv_position_reset_44e9ba"}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm",flag,str(path)],text=True).splitlines()}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_clean_44d878.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    defined=symbols(BASE,"--defined-only")
    if not PROVIDERS<=defined or "audio_uart_page_44d878" in defined:
        raise RuntimeError("page clean provider/definition contract changed")
    linked=OUT/"apollo-main-page-clean-44d878.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!={"audio_uart_page_44d878"} or after-before!=LOWER or \
            "audio_uart_page_44d878" not in symbols(linked,"--defined-only"):
        raise RuntimeError("page clean link contract changed")
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_CLEAN_ORACLE" or \
            oracle["cases"]!=192 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("page clean oracle changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_CLEAN_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "existing_providers":sorted(PROVIDERS),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(before-after),"imports_added":sorted(after-before),
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["192 controlled native/C clean cases with lower calls modeled.",
                       "Child deletion and position reset need C ownership.",
                       "Full lifecycle, allocator effects, layout and hardware remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))


if __name__=="__main__":main()
