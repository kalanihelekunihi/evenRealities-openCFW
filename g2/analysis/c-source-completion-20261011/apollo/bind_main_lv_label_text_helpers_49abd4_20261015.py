#!/usr/bin/env python3
"""Bind native-checked LV label text length and copy helpers into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_label_text_helpers_49abd4.c"
ORACLE=G2/"build/c-firmware/20261015/main-lv-label-text-helpers-49abd4/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-lv-label-set-text-49942e/apollo-main-lv-label-set-text-49942e.o"
OUT=G2/"build/c-firmware/20261015/main-lv-label-text-helpers-49abd4"
OWNED={"audio_uart_page_text_length_49abd4","audio_uart_page_text_content_init_49abe0"}
IMPORTS={"audio_uart_lv_string_length_454768","strcpy"}
BODIES={"audio_uart_page_text_length_49abd4":"1d31a19789954fb68f95b6b15403db602a4d1765f3fb1d8ec7f8532dd95898c1",
        "audio_uart_page_text_content_init_49abe0":"979fc2a86d6774e2f9944e833cafc74f0d67bec88270045b538bec9bda662676"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}

def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle["status"]!="PASS_NATIVE_MAIN_LV_LABEL_TEXT_HELPERS_49ABD4" or \
       oracle["cases"]!=10 or oracle["source_sha256"]!=sha(SOURCE) or \
       oracle["native_body_sha256"]!=BODIES or \
       set(oracle["source_owned_symbols"])!=OWNED:
        raise RuntimeError("Native LV label helper evidence changed")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_label_text_helpers_49abd4.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
        raise RuntimeError("LV label helper object contract changed")
    before=symbols(BASE,"-u")
    if len(before)!=223 or not OWNED<=before or \
       not IMPORTS<=symbols(BASE,"--defined-only"):
        raise RuntimeError("LV label helper base contract changed")
    linked=OUT/"apollo-main-lv-label-text-helpers-49abd4.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before-after!=OWNED or after-before or len(after)!=221:
        raise RuntimeError("LV label helper link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_LABEL_TEXT_HELPERS_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
             "oracle_cases":oracle["cases"],"native_body_sha256":BODIES,
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
             "imports_added":[],"unresolved_before":223,"unresolved_after":221,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Label length and content copy helpers are C-bound; label layout update, placement and hardware behavior remain unverified."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],223,221,sha(path))

if __name__=="__main__":main()
