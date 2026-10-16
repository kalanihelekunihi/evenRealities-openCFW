#!/usr/bin/env python3
"""Bind native-compared LVGL scroll movement with explicit lower gates."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_scroll_move_44e79e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-scroll-move-44e79e"
BASE=G2/"build/c-firmware/20261015/main-lv-scroll-by-44ea98/apollo-main-lv-scroll-by-44ea98.o"
ORACLE=HERE/"verify_main_lv_scroll_move_44e79e_oracle_20261015.py"
RESOLVED={"audio_uart_lv_scroll_move_44e79e"}
LOWER={"audio_uart_lv_scroll_mode_44e2a4","audio_uart_lv_scroll_top_44e4aa",
       "audio_uart_lv_scroll_dispatch_44e884"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm",flag,str(path)],text=True).splitlines()}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_scroll_move_44e79e.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    linked=OUT/"apollo-main-lv-scroll-move-44e79e.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!=RESOLVED or after-before!=LOWER or len(before)!=239 or len(after)!=241:
        raise RuntimeError("scroll movement import contract changed")
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_SCROLL_MOVE_ORACLE" or \
            oracle["cases"]!=162 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("scroll movement oracle changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_SCROLL_MOVE_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(RESOLVED),"imports_added":sorted(LOWER),
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["162 controlled native/C branch cases; nine calls controlled.",
                       "Mode, top, and dispatch bodies remain lower gates."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))

if __name__=="__main__":main()
