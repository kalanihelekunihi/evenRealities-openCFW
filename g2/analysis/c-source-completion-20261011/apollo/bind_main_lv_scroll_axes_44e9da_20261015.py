#!/usr/bin/env python3
"""Bind native-compared scroll-axis wrappers and their animation callbacks."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_scroll_axes_44e9da.c"
OUT=G2/"build/c-firmware/20261015/main-lv-scroll-axes-44e9da"
BASE=G2/"build/c-firmware/20261015/main-lv-position-reset-44e9ba/apollo-main-lv-position-reset-44e9ba.o"
ORACLE=HERE/"verify_main_lv_scroll_axes_44e9da_oracle_20261015.py"
RESOLVED={"audio_uart_lv_scroll_to_x_44e9da","audio_uart_lv_scroll_to_y_44ea04"}
LOWER={"audio_uart_lv_scroll_move_44e79e","audio_uart_lv_scroll_by_44ea98"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm",flag,str(path)],text=True).splitlines()}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_scroll_axes_44e9da.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    linked=OUT/"apollo-main-lv-scroll-axes-44e9da.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    defined=symbols(linked,"--defined-only")
    callbacks={"audio_uart_lv_scroll_anim_x_44f3b8","audio_uart_lv_scroll_anim_y_44f3d4"}
    if before-after!=RESOLVED or after-before!=LOWER or len(before)!=240 or len(after)!=240 or \
            not callbacks.issubset(defined):
        raise RuntimeError("scroll axis import/definition contract changed")
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_SCROLL_AXES_ORACLE" or \
            oracle["cases"]!=80 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("scroll axis oracle changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_SCROLL_AXES_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(RESOLVED),"imports_added":sorted(LOWER),
             "callbacks_defined":sorted(callbacks),
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["80 controlled native/C wrapper and callback cases.",
                       "Scroll movement and scroll-by bodies remain unresolved."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))

if __name__=="__main__":main()
