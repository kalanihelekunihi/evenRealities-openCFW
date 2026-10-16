#!/usr/bin/env python3
"""Bind agent-interrupt FSM action and packet encoder."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-agent-reset-5e5ed4/apollo-main-terminal-agent-reset-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-agent-interrupt-5e7068'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_agent_interrupt_5e7068.c',G2/'components/audio/uart_thread_source_candidate/terminal_agent_interrupt_encode_5cee08.c']
ORACLES=[OUT/'oracle-receipt.json',G2/'build/c-firmware/20261016/main-terminal-agent-interrupt-encode-5cee08/oracle-receipt.json']
STATUSES=['PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_INTERRUPT_C_ORACLE','PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_INTERRUPT_ENCODE_C_ORACLE']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 for s,o,status in zip(SOURCES,ORACLES,STATUSES):
  d=json.loads(o.read_text())
  if d['status']!=status or d['source_sha256']!=sha(s):raise RuntimeError('source/oracle changed')
 before=imports(BASE)
 if len(before)!=179 or 'audio_terminal_ui_action_5e7068' not in before:raise RuntimeError('Apollo frontier changed')
 objects=[]
 for s in SOURCES:
  obj=OUT/(s.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(obj)],check=True);objects.append(obj)
 linked=OUT/'apollo-main-terminal-agent-interrupt-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*[str(o) for o in objects],'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e7068'}
 if before-after!=resolved or after-before or len(after)!=178:raise RuntimeError(f'agent-interrupt binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_INTERRUPT_C','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'oracle_receipts':[str(o.relative_to(ROOT)) for o in ORACLES],'oracle_receipt_sha256':[sha(o) for o in ORACLES],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':179,'unresolved_after':178,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Agent-interrupt action and one-byte encoder pass bounded stock oracles; lower service/protobuf/LVGL/logger effects and final image remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
