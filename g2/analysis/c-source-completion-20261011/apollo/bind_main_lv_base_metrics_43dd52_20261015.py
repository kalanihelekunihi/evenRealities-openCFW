#!/usr/bin/env python3
"""Bind four native-compared Apollo base style metric wrappers."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_base_metrics_43dd52.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-metrics-43dd52"
BASE=G2/"build/c-firmware/20261015/main-lv-base-dtor-43e3de/apollo-main-lv-base-dtor-43e3de.o"
ORACLE=HERE/"verify_main_lv_base_metrics_43dd52_oracle_20261015.py"
OWNED={"audio_uart_lv_metric_43dd52","audio_uart_lv_metric_43dd5c","audio_uart_lv_metric_43dd66","audio_uart_lv_metric_43de76"}
PROVIDER={"audio_uart_lv_style_property_44bdea"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_base_metrics_43dd52.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_BASE_METRICS_ORACLE" or \
            oracle["cases"]!=48 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("base metric oracle changed")
    if not PROVIDER <= symbols(BASE,"--defined-only") or \
            symbols(obj,"-u")!=PROVIDER or symbols(obj,"--defined-only")!=OWNED:
        raise RuntimeError("base metric provider contract changed")
    linked=OUT/"apollo-main-lv-base-metrics-43dd52.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before!=after or len(before)!=234 or not OWNED <= symbols(linked,"--defined-only"):
        raise RuntimeError("base metric linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_METRICS_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Four base style selectors have native-compared C bodies; base-class event and descriptor layout remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
