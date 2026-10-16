#!/usr/bin/env python3
"""Bind the source-owned LVGL animimage factory and class record."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-ui-voice-prepare-5ebd0e/apollo-main-terminal-voice-prepare-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-anim-factory-597e90'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_anim_factory_597e90.c'
RESOLVED={'audio_terminal_voice_anim_create_597e90'};ADDED={'audio_terminal_voice_anim_ctor_597fae'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 oracle=OUT/'oracle-receipt.json';d=json.loads(oracle.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_FACTORY_C_ORACLE' or d['cases']!=3 or d['source_sha256']!=sha(SOURCE):raise RuntimeError('factory oracle changed')
 before=imports(BASE)
 if len(before)!=187 or not RESOLVED<=before:raise RuntimeError('main frontier changed')
 obj=OUT/'terminal-voice-anim-factory.o';linked=OUT/'apollo-main-terminal-voice-anim-factory-bound.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=187:raise RuntimeError(f'factory binding changed {before-after=} {after-before=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_FACTORY_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(oracle),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':187,'unresolved_after':187,'imports_resolved':sorted(RESOLVED),'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Animimage class constructor 0x597fae and voice style RAM 0x200014e8 remain unresolved; lower LVGL effects and final layout open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
