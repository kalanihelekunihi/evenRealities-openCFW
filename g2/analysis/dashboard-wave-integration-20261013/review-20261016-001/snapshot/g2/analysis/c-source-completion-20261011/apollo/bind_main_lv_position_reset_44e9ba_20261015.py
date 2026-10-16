#!/usr/bin/env python3
"""Bind native-compared LVGL position reset with lower movement gates."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_position_reset_44e9ba.c"
OUT=G2/"build/c-firmware/20261015/main-lv-position-reset-44e9ba"
BASE=G2/"build/c-firmware/20261015/main-page-clean-44d878/apollo-main-page-clean-44d878.o"
ORACLE=HERE/"verify_main_lv_position_reset_44e9ba_oracle_20261015.py"
LOWER={"audio_uart_lv_scroll_to_x_44e9da","audio_uart_lv_scroll_to_y_44ea04"}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm",flag,str(path)],text=True).splitlines()}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_position_reset_44e9ba.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    linked=OUT/"apollo-main-lv-position-reset-44e9ba.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!={"audio_uart_lv_position_reset_44e9ba"} or after-before!=LOWER:
        raise RuntimeError("position reset import contract changed")
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_POSITION_RESET_ORACLE" or \
            oracle["cases"]!=64 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("position reset oracle changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_POSITION_RESET_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(before-after),"imports_added":sorted(after-before),
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["64 controlled native/C wrapper cases.",
                       "Horizontal and vertical movement routines need C ownership.",
                       "Full scroll semantics, layout and hardware remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))


if __name__=="__main__":main()
