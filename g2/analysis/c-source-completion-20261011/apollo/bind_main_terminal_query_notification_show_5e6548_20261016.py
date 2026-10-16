#!/usr/bin/env python3
"""Bind stock-compared Terminal query-notification-show FSM action."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-lv-animimage-597ea6/apollo-main-lv-animimage-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-notification-show-5e6548'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_notification_show_5e6548.c'
ORACLE=OUT/'oracle-receipt.json'
RESOLVED={'audio_terminal_ui_action_5e6548'}
ADDED={'audio_terminal_counter_b_get_5973dc','audio_terminal_query_visibility_5ec82a'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_NOTIFICATION_SHOW_C_ORACLE' or oracle['cases']!=200 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('query-show oracle changed')
 before=imports(BASE)
 if len(before)!=187 or not RESOLVED<=before:raise RuntimeError('query-show frontier changed')
 obj=OUT/'terminal-query-notification-show.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-query-notification-show-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=188:raise RuntimeError(f'query-show linkage changed {before-after=} {after-before=}')
 r={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_NOTIFICATION_SHOW_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':187,'unresolved_after':188,'imports_resolved':sorted(RESOLVED),'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Counter getter, query-visibility and logger lower effects plus final RAM placement remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],sha(path))
if __name__=='__main__':main()
