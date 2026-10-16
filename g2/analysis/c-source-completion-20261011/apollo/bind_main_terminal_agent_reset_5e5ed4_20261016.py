#!/usr/bin/env python3
"""Bind stock-compared agent-reset FSM action."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-asr-fail-5e5de0/apollo-main-terminal-asr-fail-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-agent-reset-5e5ed4'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_agent_reset_5e5ed4.c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 oracle=OUT/'oracle-receipt.json';d=json.loads(oracle.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_RESET_C_ORACLE' or d['cases']!=75 or d['source_sha256']!=sha(SOURCE):raise RuntimeError('agent-reset oracle changed')
 before=imports(BASE)
 if len(before)!=180 or 'audio_terminal_ui_action_5e5ed4' not in before:raise RuntimeError('Apollo frontier changed')
 obj=OUT/'terminal-agent-reset.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-agent-reset-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e5ed4'}
 if before-after!=resolved or after-before or len(after)!=179:raise RuntimeError(f'agent-reset binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_RESET_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(oracle),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':180,'unresolved_after':179,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Agent-reset action passes bounded stock oracle; cleanup/LVGL/logger lower effects and final image remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
