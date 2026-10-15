#!/usr/bin/env python3
"""Bind the native-compared Apollo LV base-class event body."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2";HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_base_event_43e7d2.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-event-43e7d2"
BASE=G2/"build/c-firmware/20261015/main-lv-base-metrics-43dd52/apollo-main-lv-base-metrics-43dd52.o"
ORACLE=HERE/"verify_main_lv_base_event_43e7d2_oracle_20261015.py"
OWNED={"audio_uart_lv_base_event_43e7d2"}
ADDED={"audio_uart_lv_compass_452c66","audio_uart_lv_event_param_4519a0",
       "audio_uart_lv_input_reset_4518d8","audio_uart_lv_invalidate_area_4405d4",
       "audio_uart_lv_obj_event_state_43e442","audio_uart_lv_obj_flag_clear_43e086",
       "audio_uart_lv_obj_flag_set_43e046","audio_uart_lv_obj_is_scrolling_44d19a",
       "audio_uart_lv_obj_state_43e156","audio_uart_lv_scroll_to_view_44ea56"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_base_event_43e7d2.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_BASE_EVENT_ORACLE" or oracle["cases"]!=48 or oracle["controlled_provider_count"]!=36 or oracle["source_sha256"]!=sha(SOURCE):raise RuntimeError("base event oracle changed")
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")-symbols(BASE,"--defined-only")!=ADDED:raise RuntimeError("base event provider contract changed")
    linked=OUT/"apollo-main-lv-base-event-43e7d2.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after or after-before!=ADDED or len(before)!=234 or len(after)!=244 or not OWNED<=symbols(linked,"--defined-only"):raise RuntimeError("base event linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_EVENT_C","source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),"object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),"base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),"linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),"unresolved_before":len(before),"unresolved_after":len(after),"source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":sorted(ADDED),"source_complete":False,"full_payload_linked":False,"hardware_proof":False,"limits":["Full base-class event has a 48-case controlled native/C comparison; ten new lower imports and final class descriptor placement remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
