#!/usr/bin/env python3
"""Bind stock-compared Terminal session-status FSM action."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-agent-interrupt-5e7068/apollo-main-terminal-agent-interrupt-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-session-status-5e6018'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_session_status_5e6018.c'
ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 d=json.loads(ORACLE.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_STATUS_C_ORACLE' or d['source_sha256']!=sha(SOURCE):raise RuntimeError('source/oracle changed')
 before=imports(BASE)
 if len(before)!=178 or 'audio_terminal_ui_action_5e6018' not in before:raise RuntimeError('Apollo frontier changed')
 obj=OUT/(SOURCE.stem+'.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-session-status-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e6018'}
 if before-after!=resolved or after-before or len(after)!=177:raise RuntimeError(f'session-status binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_STATUS_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':178,'unresolved_after':177,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Session-status action passes bounded stock oracle; lower service/TD/LVGL/logger effects and final image remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
