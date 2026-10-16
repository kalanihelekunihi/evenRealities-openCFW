#!/usr/bin/env python3
"""Bind native-compared LV state getter and scrolling-chain walk."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2";HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_base_state_helpers.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-state-helpers"
BASE=G2/"build/c-firmware/20261015/main-lv-base-event-43e7d2/apollo-main-lv-base-event-43e7d2.o"
ORACLE=HERE/"verify_main_lv_base_state_helpers_oracle_20261015.py"
OWNED={"audio_uart_lv_obj_state_43e156","audio_uart_lv_obj_is_scrolling_44d19a"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_base_state_helpers.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_BASE_STATE_HELPERS_ORACLE" or oracle["cases"]!=70 or oracle["source_sha256"]!=sha(SOURCE):raise RuntimeError("state helper oracle changed")
    if symbols(obj,"-u") or symbols(obj,"--defined-only")!=OWNED:raise RuntimeError("state helper object contract changed")
    linked=OUT/"apollo-main-lv-base-state-helpers.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!=OWNED or after-before or len(before)!=244 or len(after)!=242 or not OWNED<=symbols(linked,"--defined-only"):raise RuntimeError("state helper linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_STATE_HELPERS_C","source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),"object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),"base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),"linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),"unresolved_before":len(before),"unresolved_after":len(after),"source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),"imports_added":[],"source_complete":False,"full_payload_linked":False,"hardware_proof":False,"limits":["State getter and acyclic scrolling-chain walk have bounded native-compared C bodies; live state mutation remains open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
