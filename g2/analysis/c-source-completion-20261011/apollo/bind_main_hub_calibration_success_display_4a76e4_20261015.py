#!/usr/bin/env python3
"""Bind native-checked calibration success display into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/hub_calibration_success_display_4a76e4.c"
ORACLE=G2/"build/c-firmware/20261015/main-hub-calibration-success-display-4a76e4/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-setting-notify-recalibration-49beac/apollo-main-setting-notify-recalibration-49beac.o"
OUT=G2/"build/c-firmware/20261015/main-hub-calibration-success-display-4a76e4"
OWNED={"audio_uart_hub_calibration_success_display_4a76e4"}
ADDED={"audio_uart_calibration_success_primary_200749ac",
       "audio_uart_calibration_success_secondary_200749b0"}
IMPORTS=ADDED|{"audio_uart_lv_obj_width_43fd9e","audio_uart_page_43f0e0",
               "audio_uart_page_43f506","audio_uart_page_43f66c",
               "audio_uart_page_45fffe","audio_uart_page_460084",
               "audio_uart_page_49942e"}
BODY_SHA="1f9abcc1ea1de3d7ac1fe3f0499f845eadf77e983e59061d578b2d8f199888bc"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}

def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle["status"]!="PASS_NATIVE_MAIN_HUB_CALIBRATION_SUCCESS_DISPLAY_4A76E4" or \
       oracle["cases"]!=20 or oracle["source_sha256"]!=sha(SOURCE) or \
       oracle["native_body_sha256"]!=BODY_SHA:
        raise RuntimeError("Native calibration success evidence changed")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"hub_calibration_success_display_4a76e4.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
        raise RuntimeError("Calibration success object contract changed")
    before=symbols(BASE,"-u")
    if len(before)!=219 or not OWNED<=(before) or \
       not (IMPORTS-ADDED-{"audio_uart_page_49942e"})<=symbols(BASE,"--defined-only") or \
       "audio_uart_page_49942e" not in before:
        raise RuntimeError("Calibration success base contract changed")
    linked=OUT/"apollo-main-hub-calibration-success-display-4a76e4.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before-after!=OWNED or after-before!=ADDED or len(after)!=220:
        raise RuntimeError("Calibration success link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_HUB_CALIBRATION_SUCCESS_DISPLAY_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
             "oracle_cases":oracle["cases"],"native_body_sha256":BODY_SHA,
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
             "imports_added":sorted(ADDED),"unresolved_before":219,"unresolved_after":220,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Two calibration object slots and text setter remain imported; final placement and hardware behavior remain unverified."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],219,220,sha(path))

if __name__=="__main__":main()
