#!/usr/bin/env python3
"""Bind stock-compared voice-stop action and processing label helper."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-voice-frames-200014e8/apollo-main-terminal-voice-frames-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-voice-stop-5e598a'
SOURCES=[G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_voice_stop_5e598a.c',G2/'components/audio/uart_thread_source_candidate/terminal_ui_processing_label_5ebfe0.c']
ORACLES=[OUT/'oracle-receipt.json',G2/'build/c-firmware/20261016/main-terminal-ui-processing-label-5ebfe0/oracle-receipt.json']
STATUSES=['PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_STOP_C_ORACLE','PASS_EXPERIMENTAL_MAIN_TERMINAL_PROCESSING_LABEL_C_ORACLE']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 for s,o,status in zip(SOURCES,ORACLES,STATUSES):
  d=json.loads(o.read_text())
  if d['status']!=status or d['source_sha256']!=sha(s):raise RuntimeError('oracle/source changed')
 before=imports(BASE)
 if len(before)!=185 or 'audio_terminal_ui_action_5e598a' not in before:raise RuntimeError('Apollo frontier changed')
 objects=[]
 for s in SOURCES:
  obj=OUT/(s.stem+'.o');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(s),'-o',str(obj)],check=True);objects.append(obj)
 linked=OUT/'apollo-main-terminal-ui-action-voice-stop-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*[str(o) for o in objects],'-o',str(linked)],check=True)
 after=imports(linked);resolved={'audio_terminal_ui_action_5e598a'}
 if before-after!=resolved or after-before or len(after)!=184:raise RuntimeError(f'voice-stop binding changed {before-after=} {after-before=} {len(after)=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_STOP_C','sources':[str(s.relative_to(ROOT)) for s in SOURCES],'source_sha256':[sha(s) for s in SOURCES],'oracle_receipts':[str(o.relative_to(ROOT)) for o in ORACLES],'oracle_receipt_sha256':[sha(o) for o in ORACLES],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':185,'unresolved_after':184,'imports_resolved':sorted(resolved),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Bounded stock call-sequence oracles prove this FSM action and processing-label helper only; final scatter/linker, lower LVGL effects, whole image and hardware remain open.']}
 p=OUT/'receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(p))
if __name__=='__main__':main()
