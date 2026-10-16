#!/usr/bin/env python3
"""Bind input-confirm action and its two TD source children."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-result-area-5ebff8/apollo-main-terminal-result-area-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-input-confirm-5e5bc6'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_input_confirm_5e5bc6.c',G2/'components/audio/uart_thread_source_candidate/td_record_status_set_current_597452.c',G2/'components/audio/uart_thread_source_candidate/td_session_activate_597596.c']
ORACLES=[OUT/'oracle-receipt.json',G2/'build/c-firmware/20261016/main-td-record-status-set-current-597452/oracle-receipt.json',G2/'build/c-firmware/20261016/main-td-session-activate-597596/oracle-receipt.json']
STATUSES=['PASS_EXPERIMENTAL_MAIN_TERMINAL_INPUT_CONFIRM_C_ORACLE','PASS_EXPERIMENTAL_MAIN_TD_RECORD_STATUS_SET_CURRENT_C_ORACLE','PASS_EXPERIMENTAL_MAIN_TD_SESSION_ACTIVATE_C_ORACLE']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 for s,o,status in zip(SOURCES,ORACLES,STATUSES):
  d=json.loads(o.read_text())
  if d['status']!=status or d['source_sha256']!=sha(s):raise RuntimeError('source/oracle changed')
 before=imports(BASE)
 if len(before)!=183 or 'audio_terminal_ui_action_5e5bc6' not in before:raise RuntimeError('Apollo frontier changed')
 objects=[]
 for s in SOURCES:
  obj=OUT/(s.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(obj)],check=True);objects.append(obj)
 linked=OUT/'apollo-main-terminal-input-confirm-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*[str(o) for o in objects],'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e5bc6'}
 if before-after!=resolved or after-before or len(after)!=182:raise RuntimeError(f'input-confirm binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_INPUT_CONFIRM_C','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'oracle_receipts':[str(o.relative_to(ROOT)) for o in ORACLES],'oracle_receipt_sha256':[sha(o) for o in ORACLES],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':183,'unresolved_after':182,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Action and TD child state/log branches pass bounded stock oracles; downstream service effects, final RAM/layout and whole image remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
