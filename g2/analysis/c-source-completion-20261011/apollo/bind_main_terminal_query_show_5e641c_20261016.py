#!/usr/bin/env python3
"""Bind query-show FSM action and stock-compared hit-test facade."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-agent-done-5e6268/apollo-main-terminal-agent-done-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-query-show-5e641c'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_query_show_5e641c.c',G2/'components/audio/uart_thread_source_candidate/terminal_query_hit_test_5eb61e.c']
ORACLES=[OUT/'oracle-receipt.json',G2/'build/c-firmware/20261016/main-terminal-query-hit-test-5eb61e/oracle-receipt.json']
STATUSES=['PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SHOW_C_ORACLE','PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_HIT_TEST_C_ORACLE']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 for s,o,status in zip(SOURCES,ORACLES,STATUSES):
  d=json.loads(o.read_text())
  if d['status']!=status or d['source_sha256']!=sha(s):raise RuntimeError('source/oracle changed')
 before=imports(BASE)
 if len(before)!=176 or 'audio_terminal_ui_action_5e641c' not in before:raise RuntimeError('Apollo frontier changed')
 objects=[]
 for s in SOURCES:
  obj=OUT/(s.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(obj)],check=True);objects.append(obj)
 linked=OUT/'apollo-main-terminal-query-show-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*[str(o) for o in objects],'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e641c'};added={'audio_terminal_query_construct_5eb8da','audio_terminal_query_hit_count_5eb576'}
 if before-after!=resolved or after-before!=added or len(after)!=177:raise RuntimeError(f'query-show binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SHOW_C','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'oracle_receipts':[str(o.relative_to(ROOT)) for o in ORACLES],'oracle_receipt_sha256':[sha(o) for o in ORACLES],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':176,'unresolved_after':177,'imports_resolved':sorted(resolved),'imports_added':sorted(added),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Query-show action and hit-test facade pass bounded stock oracles; constructor and hit-count children, lower LVGL/logger effects and final image remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
