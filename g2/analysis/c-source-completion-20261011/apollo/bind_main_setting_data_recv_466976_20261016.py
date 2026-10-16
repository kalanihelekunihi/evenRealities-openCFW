#!/usr/bin/env python3
"""Bind native-checked Setting data receive routing into Main."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_data_recv_handler_466976.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-data-recv-466976/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-setting-common-data-4668ae/apollo-main-setting-common-data-4668ae.o"
OUT=G2/"build/c-firmware/20261015/main-setting-data-recv-466976"
OWNED={"audio_setting_process_data_466976"}
ADDED={"audio_setting_dispatch_message_466abc",
       "audio_setting_serialize_response_49b900",
       "audio_setting_serialize_local_response_49ba58"}
IMPORTS=ADDED|{"audio_log_flags","audio_log_extended","compressed_log_output"}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}
def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_DATA_RECV_466976" or \
       oracle["cases"]!=180 or oracle["source_sha256"]!=sha(SOURCE) or \
       oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Setting data receive evidence changed")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"setting_data_recv_handler_466976.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                    "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
        raise RuntimeError("Setting data receive object contract changed")
    before=symbols(BASE,"-u")
    if len(before)!=190 or not OWNED<=before or \
       not (IMPORTS-ADDED)<=symbols(BASE,"--defined-only"):
        raise RuntimeError("Setting data receive base contract changed")
    linked=OUT/"apollo-main-setting-data-recv-466976.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before-after!=OWNED or after-before!=ADDED or len(after)!=192:
        raise RuntimeError("Setting data receive link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_DATA_RECV_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
             "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
             "imports_added":sorted(ADDED),"unresolved_before":190,"unresolved_after":192,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["The message dispatcher and two serializers are explicit imports; final placement and hardware behavior remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],190,192,sha(path))
if __name__=="__main__":main()
