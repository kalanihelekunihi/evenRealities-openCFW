#!/usr/bin/env python3
"""Bind five Terminal ABI adapters to existing stock-address C providers."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-clear-flag-alias-43dfa4/apollo-main-terminal-clear-flag-alias-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-object-abi-aliases'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_object_abi_aliases_20261016.c'
ORACLE=OUT/'oracle-receipt.json'
ALIASES={'audio_lv_object_call_43ded4','audio_lv_object_call_441488','audio_lv_object_call_450500','audio_lv_object_release_44d7b8','audio_lv_object_size_call_43f4c0'}
PROVIDERS={'audio_uart_page_43ded4','audio_uart_display_audio_reset_441488','audio_uart_lv_style_unlink_450500','audio_uart_page_delete_event_filter_44d7b8','audio_uart_page_43f4c0'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_OBJECT_ABI_ALIASES_ORACLE' or oracle['cases']!=135 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('object adapter oracle changed')
 before=symbols(BASE,'-u')
 if len(before)!=196 or not ALIASES<=before or not PROVIDERS<=symbols(BASE,'--defined-only'):raise RuntimeError('object adapter frontier changed')
 obj=OUT/'terminal-object-abi-aliases.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-object-abi-aliases-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!=ALIASES or after-before or len(after)!=191:raise RuntimeError(f'object adapter linkage changed {before-after=} {after-before=}')
 r={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_OBJECT_ABI_ALIASES_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':196,'unresolved_after':191,'imports_resolved':sorted(ALIASES),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Five adapters reuse previously C-bound providers; final placement open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],sha(path))
if __name__=='__main__':main()
