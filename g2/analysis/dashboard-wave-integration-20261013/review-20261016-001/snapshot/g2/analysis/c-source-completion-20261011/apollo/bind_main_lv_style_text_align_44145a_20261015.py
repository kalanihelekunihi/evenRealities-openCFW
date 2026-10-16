#!/usr/bin/env python3
"""Bind native-checked LV style 0x5e wrapper into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_style_text_align_44145a.c"
ORACLE=G2/"build/c-firmware/20261015/main-lv-style-text-align-44145a/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-hub-calibration-labels-update-4a7440/apollo-main-hub-calibration-labels-update-4a7440.o"
OUT=G2/"build/c-firmware/20261015/main-lv-style-text-align-44145a"
OWNED={"audio_uart_page_44145a"}
IMPORTS={"audio_uart_page_style_apply_44be4c"}
BODY_SHA="cdc616ef53e53f7c9d0f29fd780112d14541913ca157f344741fbfcd6520fd0c"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}

def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle["status"]!="PASS_NATIVE_MAIN_LV_STYLE_TEXT_ALIGN_44145A" or \
       oracle["cases"]!=24 or oracle["source_sha256"]!=sha(SOURCE) or \
       oracle["native_body_sha256"]!=BODY_SHA:
        raise RuntimeError("Native style wrapper evidence changed")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_style_text_align_44145a.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
        raise RuntimeError("Style wrapper object contract changed")
    before=symbols(BASE,"-u")
    if len(before)!=220 or OWNED&before or not IMPORTS<=symbols(BASE,"--defined-only"):
        raise RuntimeError("Style wrapper base contract changed")
    linked=OUT/"apollo-main-lv-style-text-align-44145a.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before!=after or len(after)!=220:
        raise RuntimeError("Style wrapper link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_STYLE_TEXT_ALIGN_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
             "oracle_cases":oracle["cases"],"native_body_sha256":BODY_SHA,
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":[],
             "unresolved_before":220,"unresolved_after":220,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["0x5e style wrapper is source-owned for calibration display composition; final placement and hardware behavior remain unverified."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],220,220,sha(path))

if __name__=="__main__":main()
