#!/usr/bin/env python3
"""Bind stock 0x5973dc counter getter through existing C-owned data provider."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-query-notification-show-5e6548/apollo-main-terminal-query-notification-show-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-counter-b-alias-5973dc'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_counter_b_alias_5973dc.c'
ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_COUNTER_B_ALIAS_ORACLE' or oracle['cases']!=7 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('counter oracle changed')
 before=symbols(BASE,'-u')
 if len(before)!=188 or 'audio_terminal_counter_b_get_5973dc' not in before or 'audio_td_counter_b_get' not in symbols(BASE,'--defined-only'):raise RuntimeError('counter frontier changed')
 obj=OUT/'terminal-counter-b-alias.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-counter-b-alias-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!={'audio_terminal_counter_b_get_5973dc'} or after-before or len(after)!=187:raise RuntimeError('counter linkage changed')
 r={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_COUNTER_B_ALIAS_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':188,'unresolved_after':187,'imports_resolved':['audio_terminal_counter_b_get_5973dc'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Counter getter reuses source-owned TD state; final RAM placement/init open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],sha(path))
if __name__=='__main__':main()
