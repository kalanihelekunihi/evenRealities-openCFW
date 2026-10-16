#!/usr/bin/env python3
"""Bind controlled native-compared Apollo render-task cleanup."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_render_task_free_4848e8.c"
OUT=G2/"build/c-firmware/20261015/main-lv-render-task-free-4848e8"
BASE=G2/"build/c-firmware/20261015/main-lv-render-task-evaluate-48458e/apollo-main-lv-render-task-evaluate-48458e.o"
ORACLE=HERE/"verify_main_lv_render_task_free_4848e8_oracle_20261015.py"
OWNED={"audio_uart_lv_render_task_free_4848e8","audio_uart_lv_draw_task_image_desc_489fc8"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path,mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",mode,str(path)],text=True).splitlines()}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_render_task_free_4848e8.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_FREE_ORACLE" or \
       oracle["cases"]!=48 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("render task cleanup oracle changed")
    lower=symbols(obj,"-u")
    if symbols(obj,"--defined-only")!=OWNED or lower!={
        "audio_uart_lv_area_height_4515a4","audio_uart_font_bitmap_release",
        "audio_uart_lv_heap_free","audio_uart_lvgl_log"}:
        raise RuntimeError("render task cleanup object contract changed")
    if not lower<=symbols(BASE,"--defined-only"):
        raise RuntimeError("render task cleanup lower provider absent")
    linked=OUT/"apollo-main-lv-render-task-free-4848e8.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!={"audio_uart_lv_render_task_free_4848e8"} or after-before or \
       len(before)!=237 or len(after)!=236 or not OWNED<=symbols(linked,"--defined-only"):
        raise RuntimeError("render task cleanup linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_FREE_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":237,"unresolved_after":236,
             "source_owned_symbols":sorted(OWNED),
             "imports_resolved":["audio_uart_lv_render_task_free_4848e8"],
             "imports_added":[],"source_complete":False,"full_payload_linked":False,
             "hardware_proof":False,
             "limits":["Cleanup memory and controlled providers are native-compared; live allocation and display behavior remain open."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))

if __name__=="__main__":main()
