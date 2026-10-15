#!/usr/bin/env python3
"""Bind native-compared Apollo LV object state application into Main."""
import hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_obj_state_apply_43ebec.c"
OUT=G2/"build/c-firmware/20261015/main-lv-obj-state-apply-43ebec"
BASE=G2/"build/c-firmware/20261015/main-lv-area-transform-451082/apollo-main-lv-area-transform-451082.o"
ORACLE=HERE/"verify_main_lv_obj_state_apply_43ebec_oracle_20261015.py"
OWNED={"audio_uart_lv_obj_state_apply_43ebec"}
ADDED={"audio_uart_lv_state_transition_kind_44c178",
       "audio_uart_lv_style_reference_43dce0",
       "audio_uart_lv_state_property_refresh_44bfae"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path,mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",mode,str(path)],text=True).splitlines()}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_obj_state_apply_43ebec.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_OBJ_STATE_APPLY_ORACLE" or \
       oracle["cases"]!=72 or oracle["controlled_provider_count"]!=9 or \
       oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("state apply oracle changed")
    lower=symbols(obj,"-u")
    if symbols(obj,"--defined-only")!=OWNED or lower!={
        "audio_uart_display_size_changed","audio_uart_lv_heap_alloc",
        "audio_uart_lv_heap_free","audio_uart_lv_refresh_draw_452d42",
        "audio_uart_lv_update_layer_44c50e","audio_uart_page_style_refresh_44bc8c",*ADDED}:
        raise RuntimeError("state apply object contract changed")
    if not lower-ADDED<=symbols(BASE,"--defined-only"):
        raise RuntimeError("state apply lower provider absent")
    linked=OUT/"apollo-main-lv-obj-state-apply-43ebec.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!=OWNED or after-before!=ADDED or \
       len(before)!=234 or len(after)!=236:
        raise RuntimeError("state apply linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_OBJ_STATE_APPLY_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":234,"unresolved_after":236,
             "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
             "imports_added":sorted(ADDED),"source_complete":False,
             "full_payload_linked":False,"hardware_proof":False,
             "limits":["State mutation and style-list handling are compared with controlled lower providers.",
                       "Live style selection, property refresh and transition-kind providers remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))

if __name__=="__main__":main()
