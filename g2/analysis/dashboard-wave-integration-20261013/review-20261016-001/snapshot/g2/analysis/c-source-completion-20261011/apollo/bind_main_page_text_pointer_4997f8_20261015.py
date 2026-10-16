#!/usr/bin/env python3
"""Bind the native-compared Apollo page text-pointer getter."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_text_pointer_4997f8.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-pointer-4997f8"
BASE=G2/"build/c-firmware/20261015/main-page-invalidate-440656/apollo-main-page-invalidate-440656.o"
ORACLE=HERE/"verify_main_page_text_pointer_4997f8_oracle_20261015.py"
OWNED={"audio_uart_page_text_pointer_4997f8"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_text_pointer_4997f8.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_POINTER_ORACLE" or oracle["cases"]!=8 or oracle["source_sha256"]!=sha(SOURCE):raise RuntimeError("text pointer oracle changed")
    if symbols(obj,"-u") or symbols(obj,"--defined-only")!=OWNED:raise RuntimeError("text pointer object contract changed")
    linked=OUT/"apollo-main-page-text-pointer-4997f8.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before!=after or len(before)!=235 or not OWNED<=symbols(linked,"--defined-only"):raise RuntimeError("text pointer linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_POINTER_C","source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),"object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),"base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),"linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),"unresolved_before":len(before),"unresolved_after":len(after),"source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":[],"source_complete":False,"full_payload_linked":False,"hardware_proof":False,"limits":["Text pointer getter has a native-compared C body; text ownership, full layout update and live page state remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
