#!/usr/bin/env python3
"""Bind native-compared Apollo LV draw-task renderer into Main."""
import hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_draw_task_render_451c6e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-draw-task-render-451c6e"
BASE=G2/"build/c-firmware/20261015/main-lv-image-descriptor-init-489f5e/apollo-main-lv-image-descriptor-init-489f5e.o"
ORACLE=HERE/"verify_main_lv_draw_task_render_451c6e_oracle_20261015.py"
OWNED={"audio_uart_lv_draw_task_render_451c6e"}
ADDED={"audio_uart_lv_area_transform_451082"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path,mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",mode,str(path)],text=True).splitlines()}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_draw_task_render_451c6e.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_RENDER_ORACLE" or \
       oracle["cases"]!=18 or oracle["controlled_provider_count"]!=13 or \
       oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("LV renderer oracle changed")
    lower=symbols(obj,"-u")
    if symbols(obj,"--defined-only")!=OWNED or lower!={
        "audio_uart_ambiq_area_move_450bb2","audio_uart_ambiq_image_options_init_488918",
        "audio_uart_lv_area_expand_450b98","audio_uart_lv_draw_descriptor_init_451c3a",
        "audio_uart_lv_image_descriptor_init_489f5e","audio_uart_lv_image_header_488f6a",
        "audio_uart_lv_image_source_type_488cb8","audio_uart_lv_malloc",
        "audio_uart_lv_render_task_alloc_4843ee","audio_uart_lv_render_task_queue_484476",
        "audio_uart_lvgl_log","audio_uart_page_event_calculate_489546",*ADDED}:
        raise RuntimeError("LV renderer object contract changed")
    if not lower-ADDED<=symbols(BASE,"--defined-only"):
        raise RuntimeError("LV renderer lower provider absent")
    linked=OUT/"apollo-main-lv-draw-task-render-451c6e.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!=OWNED or after-before!=ADDED or \
       len(before)!=235 or len(after)!=235:
        raise RuntimeError("LV renderer linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_RENDER_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":235,"unresolved_after":235,
             "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
             "imports_added":sorted(ADDED),"source_complete":False,
             "full_payload_linked":False,"hardware_proof":False,
             "limits":["Five task branches and allocation-failure logger entry are native-compared under controlled providers.",
                       "Live area transform, image decoder, display dispatch and fatal-loop behavior remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))

if __name__=="__main__":main()
