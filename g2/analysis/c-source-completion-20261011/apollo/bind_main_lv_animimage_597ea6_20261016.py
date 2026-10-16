#!/usr/bin/env python3
"""Bind four stock-compared LVGL animimage routines."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-object-abi-aliases/apollo-main-terminal-object-abi-aliases-bound.o'
OUT=G2/'build/c-firmware/20261016/main-lv-animimage-597ea6'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_lv_animimage_597ea6.c'
ORACLE=OUT/'oracle-receipt.json'
RESOLVED={'audio_lv_label_style_call_597ea6','audio_lv_label_style_call_597ee0','audio_lv_label_style_call_597f10','audio_lv_label_style_call_597f52'}
LOWER={'audio_uart_lv_anim_start_450408','audio_uart_lv_anim_values_4506ce'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_MAIN_LV_ANIMIMAGE_C_ORACLE' or oracle['cases']!=68 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('animimage oracle changed')
 before=symbols(BASE,'-u')
 if len(before)!=191 or not RESOLVED<=before or not LOWER<=symbols(BASE,'--defined-only'):raise RuntimeError('animimage frontier changed')
 obj=OUT/'display-lv-animimage.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-lv-animimage-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!=RESOLVED or after-before or len(after)!=187:raise RuntimeError(f'animimage linkage changed {before-after=} {after-before=}')
 r={'status':'PASS_EXPERIMENTAL_MAIN_LV_ANIMIMAGE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':191,'unresolved_after':187,'imports_resolved':sorted(RESOLVED),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Real animation lower effects and final placement remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],sha(path))
if __name__=='__main__':main()
