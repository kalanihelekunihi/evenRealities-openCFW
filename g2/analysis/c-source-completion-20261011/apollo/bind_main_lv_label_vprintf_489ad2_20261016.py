#!/usr/bin/env python3
"""Bind stock-compared LVGL formatted text allocator."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-label-text-fmt-49954c/apollo-main-terminal-label-text-fmt-bound.o'
OUT=G2/'build/c-firmware/20261016/main-lv-label-vprintf-489ad2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_lv_label_vprintf_489ad2.c'
ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def defined(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_MAIN_LV_LABEL_VPRINTF_C_ORACLE' or oracle['cases']!=60 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('text allocator oracle changed')
 before=imports(BASE)
 if len(before)!=198 or 'audio_uart_lv_label_vprintf_489ad2' not in before or 'audio_uart_lv_vsnprintf_483fea' not in defined(BASE):raise RuntimeError('text allocator frontier changed')
 obj=OUT/'display-lv-label-vprintf.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-lv-label-vprintf-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!={'audio_uart_lv_label_vprintf_489ad2'} or after-before or len(after)!=197:raise RuntimeError('text allocator linkage changed')
 r={'status':'PASS_EXPERIMENTAL_MAIN_LV_LABEL_VPRINTF_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':198,'unresolved_after':197,'imports_resolved':['audio_uart_lv_label_vprintf_489ad2'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Allocation failure trap and real formatter effects open; final placement open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],sha(path))
if __name__=='__main__':main()
