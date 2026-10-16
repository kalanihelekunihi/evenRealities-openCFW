#!/usr/bin/env python3
"""Bind the native-compared Apollo generic page factory."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_factory_43de82.c"
OUT=G2/"build/c-firmware/20261015/main-page-factory-43de82"
BASE=G2/"build/c-firmware/20261015/main-page-text-align-49ac4a/apollo-main-page-text-align-49ac4a.o"
ORACLE=HERE/"verify_main_page_factory_43de82_oracle_20261015.py"
CLASS=G2/"components/audio/uart_thread_source_candidate/display_lv_base_class_7564f8.c"
OWNED={"audio_uart_page_43de82"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_factory_43de82.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_43DE82_ORACLE" or oracle["cases"]!=6 or oracle["source_sha256"]!=sha(SOURCE) or oracle["class_source_sha256"]!=sha(CLASS):raise RuntimeError("page factory oracle changed")
    if symbols(obj,"-u")!={"audio_uart_page_create_44cf98","audio_uart_page_initialize_44d0f0","audio_uart_lv_base_class_7564f8"} or symbols(obj,"--defined-only")!=OWNED:raise RuntimeError("page factory object contract changed")
    linked=OUT/"apollo-main-page-factory-43de82.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!={"audio_uart_page_43de82"} or after-before!={"audio_uart_lv_base_class_7564f8"} or len(before)!=235 or len(after)!=235 or not OWNED<=symbols(linked,"--defined-only"):raise RuntimeError("page factory linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_43DE82_C","source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),"class_source":str(CLASS.relative_to(ROOT)),"class_source_sha256":sha(CLASS),"object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),"base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),"linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),"unresolved_before":len(before),"unresolved_after":len(after),"source_owned_symbols":sorted(OWNED),"imports_resolved":["audio_uart_page_43de82"],"imports_added":["audio_uart_lv_base_class_7564f8"],"source_complete":False,"full_payload_linked":False,"hardware_proof":False,"limits":["Factory uses a relocatable source-owned base-class descriptor; final stock ROM placement remains open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
