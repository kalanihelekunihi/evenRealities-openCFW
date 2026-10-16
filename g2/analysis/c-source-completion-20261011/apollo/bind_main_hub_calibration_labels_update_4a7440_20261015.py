#!/usr/bin/env python3
"""Bind native-checked calibration label style helper into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/hub_calibration_labels_update_4a7440.c"
ORACLE=G2/"build/c-firmware/20261015/main-hub-calibration-labels-update-4a7440/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-hub-calibration-success-display-4a76e4/apollo-main-hub-calibration-success-display-4a76e4.o"
OUT=G2/"build/c-firmware/20261015/main-hub-calibration-labels-update-4a7440"
OWNED={"audio_uart_hub_calibration_labels_update_4a7440"}
IMPORTS={"audio_uart_page_44122a","audio_uart_page_441238",
         "audio_uart_page_44120e","audio_uart_page_44121c"}
BODY_SHA="cb99dca833662dee05ac9b2a7d4054e00db2c251355d24bcd1d3fb3fa9bfd48b"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}

def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle["status"]!="PASS_NATIVE_MAIN_HUB_CALIBRATION_LABELS_UPDATE_4A7440" or \
       oracle["cases"]!=4 or oracle["source_sha256"]!=sha(SOURCE) or \
       oracle["native_body_sha256"]!=BODY_SHA:
        raise RuntimeError("Native calibration labels evidence changed")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"hub_calibration_labels_update_4a7440.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
        raise RuntimeError("Calibration labels object contract changed")
    before=symbols(BASE,"-u")
    if len(before)!=220 or OWNED&before or not IMPORTS<=symbols(BASE,"--defined-only"):
        raise RuntimeError("Calibration labels base contract changed")
    linked=OUT/"apollo-main-hub-calibration-labels-update-4a7440.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before!=after or len(after)!=220:
        raise RuntimeError("Calibration labels link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_HUB_CALIBRATION_LABELS_UPDATE_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
             "oracle_cases":oracle["cases"],"native_body_sha256":BODY_SHA,
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":[],
             "unresolved_before":220,"unresolved_after":220,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Helper is source-owned for a future calibration display update provider; final placement and hardware behavior remain unverified."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],220,220,sha(path))

if __name__=="__main__":main()
