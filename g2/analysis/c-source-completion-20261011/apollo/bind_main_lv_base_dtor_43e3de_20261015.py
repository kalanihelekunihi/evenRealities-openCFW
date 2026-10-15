#!/usr/bin/env python3
"""Bind the native-compared Apollo page LV base destructor."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_base_dtor_43e3de.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-dtor-43e3de"
BASE=G2/"build/c-firmware/20261015/main-lv-style-mark-45028e/apollo-main-lv-style-mark-45028e.o"
ORACLE=HERE/"verify_main_lv_base_dtor_43e3de_oracle_20261015.py"
OWNED={"audio_uart_lv_base_dtor_43e3de"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_base_dtor_43e3de.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_BASE_DTOR_ORACLE" or oracle["cases"]!=8 or oracle["source_sha256"]!=sha(SOURCE):raise RuntimeError("base destructor oracle changed")
    if symbols(obj,"-u")!={"audio_uart_lv_style_mark_45028e","audio_uart_page_lock_44bde0","audio_uart_lv_theme_refresh_44bc3a","audio_uart_lv_style_unlink_450500","audio_uart_lv_obj_group_43e1be","audio_uart_page_unlink_44d3b2","audio_uart_lv_style_destroy_450228","audio_uart_lv_heap_free"} or symbols(obj,"--defined-only")!=OWNED:raise RuntimeError("base destructor object contract changed")
    linked=OUT/"apollo-main-lv-base-dtor-43e3de.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before!=after or len(before)!=234 or not OWNED<=symbols(linked,"--defined-only"):raise RuntimeError("base destructor linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_DTOR_C","source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),"object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),"base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),"linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),"unresolved_before":len(before),"unresolved_after":len(after),"source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":[],"source_complete":False,"full_payload_linked":False,"hardware_proof":False,"limits":["Base destructor has a controlled-call native-compared C body; live recursive teardown and allocator effects remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
