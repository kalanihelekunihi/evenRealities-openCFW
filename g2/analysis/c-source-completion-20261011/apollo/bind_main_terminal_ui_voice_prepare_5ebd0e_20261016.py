#!/usr/bin/env python3
"""Bind voice page constructor and its stock-compared LVGL wrappers."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-action-voice-start-5e58ba/apollo-main-terminal-voice-start-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-voice-prepare-5ebd0e'
WRAPPER_OUT=G2/'build/c-firmware/20261016/main-terminal-voice-style-wrappers'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_voice_prepare_5ebd0e.c'
WRAPPERS=G2/'components/audio/uart_thread_source_candidate/terminal_voice_style_wrappers_20261016.c'
RESOLVED={'audio_terminal_ui_voice_prepare_5ebd0e'}
ADDED={'audio_terminal_voice_style_200014e8','audio_terminal_voice_anim_create_597e90'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def compile(source,obj):subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
def main():
 a=OUT/'oracle-receipt.json';b=WRAPPER_OUT/'oracle-receipt.json';oa=json.loads(a.read_text());ob=json.loads(b.read_text())
 if oa['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_PREPARE_C_ORACLE' or oa['cases']!=16 or oa['source_sha256']!=sha(SOURCE):raise RuntimeError('voice prepare oracle changed')
 if ob['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_STYLE_WRAPPERS_C_ORACLE' or ob['cases']!=80 or ob['source_sha256']!=sha(WRAPPERS):raise RuntimeError('voice style oracle changed')
 before=imports(BASE)
 if len(before)!=186 or not RESOLVED<=before:raise RuntimeError('main frontier changed')
 obj=OUT/'terminal-voice-prepare.o';wobj=OUT/'terminal-voice-style-wrappers.o';linked=OUT/'apollo-main-terminal-voice-prepare-bound.o'
 compile(SOURCE,obj);compile(WRAPPERS,wobj)
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),str(wobj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=187:raise RuntimeError(f'voice prepare binding changed {before-after=} {after-before=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_PREPARE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'wrapper_source':str(WRAPPERS.relative_to(ROOT)),'wrapper_source_sha256':sha(WRAPPERS),'oracle_receipt':str(a.relative_to(ROOT)),'oracle_receipt_sha256':sha(a),'wrapper_oracle_receipt':str(b.relative_to(ROOT)),'wrapper_oracle_receipt_sha256':sha(b),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'wrapper_object':str(wobj.relative_to(ROOT)),'wrapper_object_sha256':sha(wobj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':186,'unresolved_after':187,'imports_resolved':sorted(RESOLVED),'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Voice animation factory 0x597e90 and RAM style 0x200014e8 need source ownership; lower LVGL/event effects isolated; final RAM/object graph and whole image remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
