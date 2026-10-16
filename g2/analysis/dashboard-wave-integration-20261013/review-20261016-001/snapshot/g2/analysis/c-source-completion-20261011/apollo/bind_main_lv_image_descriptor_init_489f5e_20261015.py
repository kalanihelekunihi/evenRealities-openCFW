#!/usr/bin/env python3
"""Bind native-compared Apollo palette and image descriptor defaults."""
import hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_image_descriptor_init_489f5e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-image-descriptor-init-489f5e"
BASE=G2/"build/c-firmware/20261015/main-lv-image-header-488f6a/apollo-main-lv-image-header-488f6a.o"
ORACLE=HERE/"verify_main_lv_image_descriptor_init_489f5e_oracle_20261015.py"
OWNED={"audio_uart_lv_image_descriptor_init_489f5e","audio_uart_lv_palette_table_716330",
       "audio_uart_page_488290"}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path,mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",mode,str(path)],text=True).splitlines()}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_image_descriptor_init_489f5e.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DESCRIPTOR_INIT_ORACLE" or \
       oracle["cases"]!=25 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("LV image descriptor oracle changed")
    lower=symbols(obj,"-u")
    if symbols(obj,"--defined-only")!=OWNED or lower!={
        "audio_uart_display_page_style","audio_uart_lvgl_log"}:
        raise RuntimeError("LV image descriptor object contract changed")
    if not lower<=symbols(BASE,"--defined-only"):
        raise RuntimeError("LV image descriptor lower provider absent")
    linked=OUT/"apollo-main-lv-image-descriptor-init-489f5e.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!={"audio_uart_page_488290"} or after-before or \
       len(before)!=236 or len(after)!=235 or not OWNED<=symbols(linked,"--defined-only"):
        raise RuntimeError("LV image descriptor linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DESCRIPTOR_INIT_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":236,"unresolved_after":235,
             "source_owned_symbols":sorted(OWNED),
             "imports_resolved":["audio_uart_page_488290"],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Palette RGB and descriptor bytes native-compared; stock palette return top byte unwritten."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))

if __name__=="__main__":main()
