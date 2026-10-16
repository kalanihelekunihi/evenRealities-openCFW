#!/usr/bin/env python3
"""Bind stock-compared Terminal formatted-label routine."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-label-text-alias-49942e/apollo-main-terminal-label-text-alias-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-label-text-fmt-49954c'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_label_text_fmt_49954c.c'
ORACLE=OUT/'oracle-receipt.json'
RESOLVED={'audio_lv_label_set_text_fmt_49954c'}
ADDED={'audio_uart_lv_label_vprintf_489ad2'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {l.split()[-1] for l in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_FMT_C_ORACLE' or oracle['cases']!=36 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('formatter oracle changed')
 before=imports(BASE)
 if len(before)!=198 or not RESOLVED<=before:raise RuntimeError('formatter frontier changed')
 obj=OUT/'terminal-label-text-fmt.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 linked=OUT/'apollo-main-terminal-label-text-fmt-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=198:raise RuntimeError(f'formatter linkage changed {before-after=} {after-before=}')
 r={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_FMT_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':198,'unresolved_after':198,'imports_resolved':sorted(RESOLVED),'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Null pointer fatal branches and real vprintf effects open; lower formatter 0x489ad2 and final placement open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(r['status'],sha(path))
if __name__=='__main__':main()
