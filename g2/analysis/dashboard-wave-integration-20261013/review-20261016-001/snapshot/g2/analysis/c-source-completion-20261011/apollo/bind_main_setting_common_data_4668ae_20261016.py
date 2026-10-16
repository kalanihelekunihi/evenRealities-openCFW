#!/usr/bin/env python3
"""Bind the native-checked Setting common-data callback into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_common_data_handler_4668ae.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-common-data-4668ae/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-tracepoint-delete-all-files-5ee650/apollo-main-tracepoint-delete-all-files-5ee650.o"
OUT=G2/"build/c-firmware/20261015/main-setting-common-data-4668ae"
OWNED={"audio_uart_registry_callback_4668ae"}
ADDED={"audio_setting_parse_data_package_49b1f8", "audio_setting_process_data_466976",
       "audio_setting_handle_command5_46bbb4"}
IMPORTS=ADDED|{"audio_log_flags","audio_log_extended","compressed_log_output",
               "audio_settings_last_message_state"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}

def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_COMMON_DATA_4668AE" or \
       oracle["cases"]!=360 or oracle["source_sha256"]!=sha(SOURCE) or \
       oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Setting common-data evidence changed")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"setting_common_data_handler_4668ae.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                    "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
        raise RuntimeError("Setting common-data object contract changed")
    before=symbols(BASE,"-u")
    if len(before)!=188 or not OWNED<=before or \
       not (IMPORTS-ADDED)<=symbols(BASE,"--defined-only"):
        raise RuntimeError("Setting common-data base contract changed")
    linked=OUT/"apollo-main-setting-common-data-4668ae.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before-after!=OWNED or after-before!=ADDED or len(after)!=190:
        raise RuntimeError("Setting common-data link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_COMMON_DATA_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
             "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
             "imports_added":sorted(ADDED),"unresolved_before":188,"unresolved_after":190,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["The parser, post-parse processor and command-5 handler are exposed imports; global RAM initialization, final placement and hardware behavior remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],188,190,sha(path))

if __name__=="__main__":main()
