#!/usr/bin/env python3
"""Bind the 19 source-owned voice animation frames and initialized RAM table."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-voice-anim-children/apollo-main-terminal-voice-anim-children-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-frames-200014e8'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_frames_200014e8.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/terminal_voice_frames_placement.ld'
RESOLVED={'audio_terminal_voice_style_200014e8'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 oracle=OUT/'oracle-receipt.json';d=json.loads(oracle.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_FRAMES_C_ORACLE' or d['stock_table_count']!=19 or d['pixel_bytes']!=4864 or d['descriptor_bytes']!=532 or d['pointer_table_bytes']!=76 or d['source_sha256']!=sha(SOURCE) or d['linker_sha256']!=sha(LINKER):raise RuntimeError('voice frame oracle changed')
 before=imports(BASE)
 if len(before)!=186 or not RESOLVED<=before:raise RuntimeError('main frontier changed')
 obj=OUT/'terminal-voice-frames.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if sha(obj)!=d['object_sha256']:raise RuntimeError('verified asset object changed')
 linked=OUT/'apollo-main-terminal-voice-frames-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!=RESOLVED or after-before or len(after)!=185:raise RuntimeError(f'voice frame binding changed {before-after=} {after-before=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_FRAMES_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'linker':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),'oracle_receipt':str(oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(oracle),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':186,'unresolved_after':185,'imports_resolved':sorted(RESOLVED),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Exact source-owned frame bytes and a bounded table placement are proven; integration with complete main scatter/linker map, LVGL effects and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
