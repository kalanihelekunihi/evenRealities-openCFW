#!/usr/bin/env python3
"""Bind native-compared Apollo animation lookup ahead of page layout."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_lv_anim_lookup_450566.c"
OUT=G2/"build/c-firmware/20261015/main-page-lv-anim-lookup-450566"
BASE=G2/"build/c-firmware/20261015/main-page-layout-metric-getters-499402/apollo-main-page-layout-metric-getters-499402.o"
ORACLE=HERE/"verify_main_page_lv_anim_lookup_450566_oracle_20261015.py"
OWNED="audio_uart_page_lv_anim_lookup_450566"
PROVIDERS={"audio_uart_display_lv_state","audio_uart_lv_list_first","audio_uart_lv_list_next"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_lv_anim_lookup_450566.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_LV_ANIM_LOOKUP_ORACLE" or \
            oracle["cases"]!=72 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("animation lookup oracle changed")
    if not PROVIDERS <= symbols(BASE,"--defined-only") or \
            symbols(obj,"-u")!=PROVIDERS or OWNED not in symbols(obj,"--defined-only"):
        raise RuntimeError("animation lookup provider contract changed")
    linked=OUT/"apollo-main-page-lv-anim-lookup-450566.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before!=after or len(before)!=235 or OWNED not in symbols(linked,"--defined-only"):
        raise RuntimeError("animation lookup linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_LV_ANIM_LOOKUP_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "source_owned_symbols":[OWNED],"imports_resolved":[],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["List traversal is controlled; full layout update and live animation registry remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
