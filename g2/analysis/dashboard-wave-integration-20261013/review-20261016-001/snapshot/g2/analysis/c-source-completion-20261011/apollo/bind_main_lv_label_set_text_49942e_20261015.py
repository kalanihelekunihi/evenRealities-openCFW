#!/usr/bin/env python3
"""Bind native-checked LV label text setter into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_label_set_text_49942e.c"
ORACLE=G2/"build/c-firmware/20261015/main-lv-label-set-text-49942e/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-hub-calibration-display-update-4a7472/apollo-main-hub-calibration-display-update-4a7472.o"
OUT=G2/"build/c-firmware/20261015/main-lv-label-set-text-49942e"
OWNED={"audio_uart_page_49942e"}
ADDED={"audio_uart_page_text_content_init_49abe0","audio_uart_page_text_length_49abd4"}
EXISTING={"audio_uart_page_layout_update_49a602"}
DEFINED={"audio_uart_lv_heap_free","audio_uart_lv_malloc","audio_uart_lv_realloc_44f76a",
         "audio_uart_lvgl_log","audio_uart_page_event_prepare_49aacc"}
BODY_SHA="3f85db497348ade2320bc3303988e53b4dea1f52f9d31c06f77bb45ceb9d7a50"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}

def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle["status"]!="PASS_NATIVE_MAIN_LV_LABEL_SET_TEXT_49942E" or \
       oracle["cases"]!=27 or oracle["source_sha256"]!=sha(SOURCE) or \
       oracle["native_body_sha256"]!=BODY_SHA:
        raise RuntimeError("Native LV label setter evidence changed")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_label_set_text_49942e.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=ADDED|EXISTING|DEFINED:
        raise RuntimeError("LV label setter object contract changed")
    before=symbols(BASE,"-u")
    if len(before)!=222 or not OWNED|EXISTING<=before or \
       not DEFINED<=symbols(BASE,"--defined-only"):
        raise RuntimeError("LV label setter base contract changed")
    linked=OUT/"apollo-main-lv-label-set-text-49942e.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before-after!=OWNED or after-before!=ADDED or len(after)!=223:
        raise RuntimeError("LV label setter link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_LABEL_SET_TEXT_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
             "oracle_cases":oracle["cases"],"native_body_sha256":BODY_SHA,
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
             "imports_added":sorted(ADDED),"unresolved_before":222,"unresolved_after":223,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Text ownership and fatal paths are C-bound; text helpers and layout update remain explicit imports; final placement and hardware behavior remain unverified."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],222,223,sha(path))

if __name__=="__main__":main()
