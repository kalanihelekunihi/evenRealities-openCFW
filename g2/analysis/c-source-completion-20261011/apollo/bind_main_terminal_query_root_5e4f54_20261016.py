#!/usr/bin/env python3
"""Bind the stock-compared Terminal query root/panel constructor."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-terminal-query-style-setters/apollo-main-terminal-query-style-setters-bound.o'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-root-5e4f54'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_root_5e4f54.c'
RESOLVED={'audio_terminal_query_root_5e4f54'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
def main():
 oracle=OUT/'oracle-receipt.json';d=json.loads(oracle.read_text())
 if d['status']!='PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_ROOT_C_ORACLE' or d['cases']!=30 or d['source_sha256']!=sha(SOURCE):raise RuntimeError('oracle changed')
 before=imports(BASE)
 if len(before)!=187 or not RESOLVED<=before:raise RuntimeError('main frontier changed')
 obj=OUT/'terminal-query-root.o';linked=OUT/'apollo-main-terminal-query-root-bound.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=imports(linked)
 if before-after!=RESOLVED or after-before or len(after)!=186:raise RuntimeError(f'root binding changed {before-after=} {after-before=}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_ROOT_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(oracle.relative_to(ROOT)),'oracle_receipt_sha256':sha(oracle),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':187,'unresolved_after':186,'imports_resolved':sorted(RESOLVED),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Query dialog/root call chain is C-bound, but underlying LVGL effects, final object graph, RAM layout and whole payload remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],sha(path))
if __name__=='__main__':main()
