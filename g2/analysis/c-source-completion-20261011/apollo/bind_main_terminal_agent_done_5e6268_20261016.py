#!/usr/bin/env python3
"""Bind stock-compared Terminal agent-done FSM action."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-session-status-5e6018/apollo-main-terminal-session-status-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-agent-done-5e6268'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_agent_done_5e6268.c'
ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 d=json.loads(ORACLE.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_DONE_C_ORACLE' or d['source_sha256']!=sha(SOURCE):raise RuntimeError('source/oracle changed')
 before=imports(BASE)
 if len(before)!=177 or 'audio_terminal_ui_action_5e6268' not in before:raise RuntimeError('Apollo frontier changed')
 obj=OUT/(SOURCE.stem+'.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-agent-done-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e6268'}
 if before-after!=resolved or after-before or len(after)!=176:raise RuntimeError(f'agent-done binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_DONE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':177,'unresolved_after':176,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Agent-done action passes bounded stock oracle; lower cleanup/LVGL/logger effects and final image remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
