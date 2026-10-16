#!/usr/bin/env python3
"""Bind stock-compared LVGL image draw descriptor initializer."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-lv-image-style-accessors-498634/apollo-main-lv-image-style-accessors-bound.o'
OUT=G2/'build/c-firmware/20261016/main-lv-image-dsc-init-452a34'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_lv_image_draw_dsc_init_452a34.c'
ORACLE=OUT/'oracle-receipt.json'
RESOLVED={'audio_uart_lv_obj_init_draw_image_452a34'}
ADDED={'audio_uart_lv_style_image_blend_45260a','audio_uart_lv_style_image_opa_4524a4','audio_uart_lv_style_image_recolor_4524b0','audio_uart_lv_style_image_recolor_opa_4524d0'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
    oracle=json.loads(ORACLE.read_text())
    if oracle['status']!='PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DSC_INIT_C_ORACLE' or oracle['cases']!=216 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('descriptor oracle changed')
    before=imports(BASE)
    if len(before)!=201 or not RESOLVED<=before:raise RuntimeError('descriptor frontier changed')
    obj=OUT/'display-lv-image-dsc-init.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    linked=OUT/'apollo-main-lv-image-dsc-init-bound.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=imports(linked)
    if before-after!=RESOLVED or after-before!=ADDED or len(after)!=204:raise RuntimeError(f'frontier changed {len(after)} {before-after=} {after-before=}')
    result={'status':'PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DSC_INIT_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':201,'unresolved_after':204,'imports_resolved':sorted(RESOLVED),'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Four exposed style getters and lower draw scheduler remain open; final placement open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],sha(path))
if __name__=='__main__':main()
