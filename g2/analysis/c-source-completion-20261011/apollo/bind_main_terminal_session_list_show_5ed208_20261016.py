#!/usr/bin/env python3
"""Bind session-list-show FSM action and two small children."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-query-construct-5eb8da/apollo-main-terminal-query-construct-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-session-list-show-5ed208'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_session_list_show_5ed208.c',G2/'components/audio/uart_thread_source_candidate/terminal_session_list_small_children_20261016.c']
ORACLES=[OUT/'oracle-receipt.json',OUT/'children-oracle-receipt.json']
STATUSES=['PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_SHOW_C_ORACLE','PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_SMALL_CHILDREN_C_ORACLE']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 for s,o,status in zip(SOURCES,ORACLES,STATUSES):
  d=json.loads(o.read_text())
  if d['status']!=status or d['source_sha256']!=sha(s):raise RuntimeError('source/oracle changed')
 before=imports(BASE)
 if len(before)!=175 or 'audio_terminal_ui_action_5ed208' not in before:raise RuntimeError('Apollo frontier changed')
 objects=[]
 for s in SOURCES:
  obj=OUT/(s.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(obj)],check=True);objects.append(obj)
 linked=OUT/'apollo-main-terminal-session-list-show-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*[str(o) for o in objects],'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5ed208'}
 added={'audio_terminal_cancel_pending_5cef8c','audio_td_flag_b_set_597572','audio_terminal_session_list_rebuild_5ecef6'}
 if before-after!=resolved or after-before!=added or len(after)!=177:raise RuntimeError(f'session-list-show binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_SHOW_C','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'oracle_receipts':[str(o.relative_to(ROOT)) for o in ORACLES],'oracle_receipt_sha256':[sha(o) for o in ORACLES],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':175,'unresolved_after':177,'imports_resolved':sorted(resolved),'imports_added':sorted(added),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Session-list action and two children pass bounded stock oracles; cancellation sender, TD flag setter and selector rebuild are exposed imports. Lower service/log effects, final image and hardware remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
