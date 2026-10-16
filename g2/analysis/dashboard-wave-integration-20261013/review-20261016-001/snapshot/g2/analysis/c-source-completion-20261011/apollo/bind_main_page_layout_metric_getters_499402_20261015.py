#!/usr/bin/env python3
"""Bind two native-compared Apollo layout style metric wrappers."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_layout_metric_getters_499402.c"
OUT=G2/"build/c-firmware/20261015/main-page-layout-metric-getters-499402"
BASE=G2/"build/c-firmware/20261015/main-page-layout-helpers-49a5c0/apollo-main-page-layout-helpers-49a5c0.o"
ORACLE=HERE/"verify_main_page_layout_metric_getters_499402_oracle_20261015.py"
OWNED={"audio_uart_page_metric_499402","audio_uart_page_metric_49940c"}
PROVIDER={"audio_uart_lv_style_property_44bdea"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_layout_metric_getters_499402.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_METRIC_GETTERS_ORACLE" or \
            oracle["cases"]!=24 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("layout metric oracle changed")
    if not PROVIDER <= symbols(BASE,"--defined-only") or \
            symbols(obj,"-u")!=PROVIDER or symbols(obj,"--defined-only")!=OWNED:
        raise RuntimeError("layout metric provider contract changed")
    linked=OUT/"apollo-main-page-layout-metric-getters-499402.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before!=after or len(before)!=235 or not OWNED <= symbols(linked,"--defined-only"):
        raise RuntimeError("layout metric linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_METRIC_GETTERS_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Two layout selectors have native-compared C bodies; style provider behavior and full layout update remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
