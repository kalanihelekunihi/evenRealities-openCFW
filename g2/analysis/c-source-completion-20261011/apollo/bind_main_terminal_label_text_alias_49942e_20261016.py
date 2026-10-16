#!/usr/bin/env python3
"""Bind Terminal's 0x49942e label-text alias to existing C provider."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-lv-draw-image-488a38/apollo-main-lv-draw-image-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-label-text-alias-49942e'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_label_text_alias_49942e.c'
ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def defined(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_ALIAS_ORACLE' or oracle['cases']!=48 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('alias oracle changed')
 before=imports(BASE)
 if len(before)!=199 or 'audio_lv_anim_start_49942e' not in before or 'audio_uart_page_49942e' not in defined(BASE):raise RuntimeError('label alias frontier changed')
 obj=OUT/'terminal-label-text-alias.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-label-text-alias-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!={'audio_lv_anim_start_49942e'} or after-before or len(after)!=198:raise RuntimeError('alias linkage changed')
 r={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_ALIAS_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':199,'unresolved_after':198,'imports_resolved':['audio_lv_anim_start_49942e'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Alias forwards to existing stock-compared label-text C provider; final placement open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],sha(path))
if __name__=='__main__':main()
